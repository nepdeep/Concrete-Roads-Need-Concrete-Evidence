"""Nepal pavement decision screening model. Python 3 stdlib only.

Run: python models/pavement_model.py
All installed rates and intervention schedules are stated assumptions, not bids.
No structural adequacy, hydraulic capacity, probability, or final design is implied.
"""
from pathlib import Path
import csv
import json
import itertools

ROOT = Path(__file__).resolve().parent
WIDTH = 7.0
AREA = WIDTH * 1000
HORIZON = 30
DISCOUNT = 0.05
STRESS_SHARE = 0.30
PROJECT_KM = 10
DESIGN_SUPERVISION = 0.05
CONTINGENCY = 0.15
VAT = 0.13


def item(id, name, unit, quantity, rate, low, high, note):
    return dict(id=id, name=name, unit=unit, quantity_per_km=quantity,
                rate_npr=rate, rate_low_npr=low, rate_high_npr=high,
                direct_cost_npr=quantity * rate, evidence="illustrative assumption", note=note)


COMMON = [
    item("formation", "Formation preparation and compaction", "m2", AREA, 150, 100, 250,
         "Existing stable alignment; excludes new embankment and deep weak-ground treatment."),
    item("gsb", "Granular subbase, 200 mm compacted", "m3", AREA*.2, 2500, 1800, 3500,
         "Illustrative quantity; same common layer in both concepts, not a design recommendation."),
    item("drains", "Side drains, both sides", "m", 2000, 3000, 2000, 5000,
         "Concept allowance for lined side drains; dimensions require catchment and outfall design."),
    item("outlets", "Cross-drain/outfall rehabilitation allowance", "allowance", 1, 1000000, 500000, 2500000,
         "No new major culverts, bridges or flood-protection structures included."),
    item("shoulders", "Shoulders, 0.75 m each side", "m2", 1500, 700, 450, 1100,
         "Shoulders are outside the equal 7 m carriageway."),
    item("safety_qa", "Signs, markings, traffic management and contractor QA", "allowance", 1,
         1500000, 1000000, 2500000, "Common initial construction allowance."),
]
FLEXIBLE = [
    item("wmm", "Wet-mix macadam, 200 mm compacted", "m3", AREA*.2, 3500, 2600, 4700,
         "Illustrative base, to be redesigned after axle counts and soaked CBR."),
    item("dbm", "Dense bituminous macadam, 60 mm", "m3", AREA*.06, 18000, 14000, 24000,
         "Installed mix assumption includes materials, local haul, plant, labour and contractor margin."),
    item("bc", "Asphalt concrete surface, 40 mm", "m3", AREA*.04, 22000, 17000, 29000,
         "Not a quoted Nepal contract rate; long haul and remote sites can exceed range."),
    item("coats", "Prime and tack coats", "m2", AREA, 120, 80, 180,
         "Combined coat allowance, not a binder application-rate specification."),
]
CONCRETE = [
    item("dlc", "Dry lean concrete subbase, 150 mm", "m3", AREA*.15, 9000, 7000, 12000,
         "Illustrative support layer; DoR requires at least 7 days before placing slab."),
    item("slab", "Jointed plain concrete slab, 250 mm", "m3", AREA*.25, 15000, 11500, 20000,
         "Includes placing and curing; flexural design and approved mix must determine thickness."),
    item("joints", "Dowels, ties, joints, sawing and sealing", "m2", AREA, 250, 170, 450,
         "Separate from slab rate to avoid omitting joints or counting them twice."),
    item("separator", "Separation membrane", "m2", AREA, 70, 45, 100,
         "Concept allowance; detailed interface specification by pavement designer."),
]

PARAMETERS = {
    "ordinary_asphalt_overlay_years": 8,
    "stressed_asphalt_overlay_years": 4,
    "overlay_cost_npr_per_km": 7250000,
    "overlay_cost_breakdown": {"40mm_asphalt_280m3_at_22000": 6160000,
                               "milling_prep_7000m2_at_120": 840000,
                               "traffic_management": 250000},
    "common_routine_npr_per_km_year": 180000,
    "asphalt_ordinary_routine_npr_per_km_year": 150000,
    "asphalt_stressed_routine_npr_per_km_year": 300000,
    "concrete_ordinary_routine_npr_per_km_year": 80000,
    "concrete_stressed_routine_npr_per_km_year": 150000,
    "concrete_joint_reseal_years": [5,10,15,20,25],
    "concrete_joint_reseal_npr_per_km": 260000,
    "concrete_slab_repair_years": [15,25],
    "concrete_ordinary_repair_share": 0.03,
    "concrete_stressed_repair_share": 0.05,
    "concrete_slab_repair_npr_per_m2": 5500,
    "hybrid_transition_allowance_npr_per_project": 1500000,
    "initial_structural_service_life_years": 30,
}


def direct(items, scale=1):
    return sum(i["direct_cost_npr"] for i in items) * scale


def pavement(kind, exposure, discount=.05, stress_overlay=4, ordinary_overlay=8,
             asphalt_factor=1, concrete_factor=1):
    """One km of a material in one exposure class, including shared work once."""
    specific = direct(FLEXIBLE, asphalt_factor) if kind == "asphalt" else direct(CONCRETE, concrete_factor)
    works = direct(COMMON) + specific
    capex = works * (1 + DESIGN_SUPERVISION)
    cashflows = [dict(year=y, construction_npr=capex if y==0 else 0,
                     routine_npr=0, periodic_npr=0, residual_credit_npr=0) for y in range(31)]
    routine = PARAMETERS[f"{kind}_{exposure}_routine_npr_per_km_year"]
    factor = asphalt_factor if kind == "asphalt" else concrete_factor
    for y in range(1,31):
        cashflows[y]["routine_npr"] = PARAMETERS["common_routine_npr_per_km_year"] + routine * factor
    events = []
    if kind == "asphalt":
        interval = stress_overlay if exposure=="stressed" else ordinary_overlay
        cost = PARAMETERS["overlay_cost_npr_per_km"] * asphalt_factor
        years = list(range(interval,30,interval))
        for year in years:
            cashflows[year]["periodic_npr"] += cost
            events.append(dict(year=year, name="Mill/prep and renew 40 mm surface", cost_npr=cost))
        last = years[-1] if years else 0
        # Initial surface uses its own BC cost if no overlay within horizon.
        remaining = max(0, interval - (30-last)) / interval
        credit = (cost if last else direct([FLEXIBLE[2]],asphalt_factor))*remaining
        cashflows[30]["residual_credit_npr"] = credit
    else:
        for year in PARAMETERS["concrete_joint_reseal_years"]:
            cost = PARAMETERS["concrete_joint_reseal_npr_per_km"]*concrete_factor
            cashflows[year]["periodic_npr"] += cost
            events.append(dict(year=year, name="Joint resealing", cost_npr=cost))
        repair_share = PARAMETERS[f"concrete_{exposure}_repair_share"]
        for year in PARAMETERS["concrete_slab_repair_years"]:
            cost = AREA * repair_share * PARAMETERS["concrete_slab_repair_npr_per_m2"]*concrete_factor
            cashflows[year]["periodic_npr"] += cost
            events.append(dict(year=year, name=f"Localized full-depth repair ({repair_share:.0%} slab area)",cost_npr=cost))
        # Repair restores the original 30-year service period; no assumed life extension.
    cumulative = 0
    for row in cashflows:
        row["net_npr"] = row["construction_npr"]+row["routine_npr"]+row["periodic_npr"]-row["residual_credit_npr"]
        row["discounted_npr"] = row["net_npr"]/(1+discount)**row["year"]
        cumulative += row["discounted_npr"]
        row["cumulative_discounted_npr"] = cumulative
    return dict(direct_works_npr=works,capex_base_npr=capex,cashflows=cashflows,
                agency_lcc_npr=cumulative,maintenance_events=events)


def combine(parts, transition=0, discount=.05):
    flows=[]
    for y in range(31):
        row={"year":y}
        for field in ("construction_npr","routine_npr","periodic_npr","residual_credit_npr","net_npr","discounted_npr","cumulative_discounted_npr"):
            row[field] = sum(weight*p["cashflows"][y][field] for weight,p in parts)
        if transition:
            if y==0:
                for field in ("construction_npr","net_npr","discounted_npr"):
                    row[field] += transition*(1+DESIGN_SUPERVISION)
            row["cumulative_discounted_npr"] += transition*(1+DESIGN_SUPERVISION)
        flows.append(row)
    works=sum(w*p["direct_works_npr"] for w,p in parts)+transition
    capex=works*(1+DESIGN_SUPERVISION)
    contingency=capex*CONTINGENCY
    vat=(capex+contingency)*VAT
    return dict(direct_works_npr=works,design_supervision_npr=works*DESIGN_SUPERVISION,
                capex_base_npr=capex,contingency_npr=contingency,vat_npr=vat,
                cash_budget_npr=capex+contingency+vat,agency_lcc_npr=flows[-1]["cumulative_discounted_npr"],cashflows=flows)


def evaluate(discount=.05,stress_share=.3,stress_overlay=4,ordinary_overlay=8,asphalt_factor=1,concrete_factor=1):
    kwargs=dict(discount=discount,stress_overlay=stress_overlay,ordinary_overlay=ordinary_overlay,
                asphalt_factor=asphalt_factor,concrete_factor=concrete_factor)
    ao=pavement("asphalt","ordinary",**kwargs)
    ast=pavement("asphalt","stressed",**kwargs)
    co=pavement("concrete","ordinary",**kwargs)
    cst=pavement("concrete","stressed",**kwargs)
    p=stress_share
    transition=PARAMETERS["hybrid_transition_allowance_npr_per_project"]/PROJECT_KM if 0<p<1 else 0
    options={"A":combine([(1-p,ao),(p,ast)]),"B":combine([(1-p,co),(p,cst)]),
             "C":combine([(1-p,ao),(p,cst)],transition=transition)}
    return options,{"asphalt_ordinary":ao,"asphalt_stressed":ast,"concrete_ordinary":co,"concrete_stressed":cst}


CRITERIA = [
    {"id":"lcc","name":"30-year agency cost","weight":20,"scores":{},"reason":"Calculated: score=5 × lowest modeled LCC / option LCC. Model uncertainty remains."},
    {"id":"capex","name":"Initial budget affordability","weight":10,"scores":{},"reason":"Calculated: score=5 × lowest base capex / option capex. Separate liquidity constraint; overlaps cost deliberately."},
    {"id":"fit","name":"Fit to a varied corridor","weight":20,"scores":{"A":3,"B":4,"C":5},"reason":"Judgment: C targets permanent high-stress locations; A less suited to assumed slow/heavy load stress; B sacrifices flexibility on ordinary stretches. Depends on successful diagnosis, drainage and stable foundations."},
    {"id":"qa","name":"Deliverability and quality control","weight":10,"scores":{"A":4.5,"B":2.5,"C":3.5},"reason":"Judgment: established asphalt supply versus additional concrete paving, joint and curing skills; C needs both and transition management."},
    {"id":"maintenance","name":"Recurring maintenance burden","weight":10,"scores":{"A":2.5,"B":4,"C":3.5},"reason":"Judgment: asphalt needs more frequent interventions under assumed service lives; concrete still needs joints, slabs and drain upkeep. Overlaps LCC only for non-cash management reliability."},
    {"id":"local","name":"Domestic supply and import exposure","weight":10,"scores":{"A":2,"B":4.5,"C":3},"reason":"Judgment: concrete uses domestic cement, with fuel/equipment/inputs still partly imported; asphalt also uses local aggregate and labour. Not a quantified foreign-exchange saving."},
    {"id":"disruption","name":"Construction access and reopening","weight":10,"scores":{"A":4.5,"B":2,"C":3.5},"reason":"Judgment: concrete new-construction 28-day traffic closure per DoR; staged partial-width work may maintain access but does not waive cure requirement."},
    {"id":"utilities","name":"Utility access and staged adaptation","weight":5,"scores":{"A":5,"B":2,"C":4},"reason":"Judgment: asphalt easier to cut, restore and strengthen; concrete most suitable after utility conflicts resolved."},
    {"id":"environment","name":"Environmental evidence","weight":5,"scores":{"A":3,"B":3,"C":3},"reason":"Neutral placeholder: no Nepal mix EPDs, haul inventory, recycling or vehicle-use model. No environmental winner claimed."},
]


def matrix(options):
    criteria=json.loads(json.dumps(CRITERIA))
    for crit,field in [(criteria[0],"agency_lcc_npr"),(criteria[1],"capex_base_npr")]:
        minimum=min(o[field] for o in options.values())
        crit["scores"]={key:5*minimum/o[field] for key,o in options.items()}
    def score(weights):
        values={key:sum(weights[c["id"]]*c["scores"][key] for c in criteria)/100 for key in options}
        return {"weights":weights,"scores":values,"ranking":sorted(values,key=values.get,reverse=True)}
    balanced={c["id"]:c["weight"] for c in criteria}
    profiles={"balanced":balanced,
              "budget_and_access":{"lcc":25,"capex":25,"fit":5,"qa":15,"maintenance":5,"local":5,"disruption":10,"utilities":5,"environment":5},
              "domestic_supply_and_maintenance":{"lcc":10,"capex":5,"fit":15,"qa":5,"maintenance":25,"local":30,"disruption":5,"utilities":0,"environment":5}}
    sensitivity=[]
    for changed in criteria:
        for weight in range(0,61,5):
            other_scale=(100-weight)/(100-balanced[changed["id"]])
            weights={k:(weight if k==changed["id"] else v*other_scale) for k,v in balanced.items()}
            result=score(weights)
            sensitivity.append({"criterion":changed["id"],"weight":weight,"winner":result["ranking"][0],"scores":result["scores"]})
    # Independent, one-cell +/-1 judgement stress; deterministic alternatives, not probabilities.
    judgment_stress=[]
    for c in criteria[2:]:
        for option in options:
            original=c["scores"][option]
            for delta in [-1,1]:
                c["scores"][option]=min(5,max(1,original+delta))
                result=score(balanced)
                judgment_stress.append(dict(criterion=c["id"],option=option,delta=delta,
                                            winner=result["ranking"][0],scores=result["scores"]))
            c["scores"][option]=original
    return {"scale":"1=poor; 5=strong. Except cost ratios, scores and all weights are subjective screening judgments.",
            "criteria":criteria,"profiles":{k:score(w) for k,w in profiles.items()},
            "one_weight_at_a_time":sensitivity,"one_score_at_a_time":judgment_stress,
            "warning":"Scores are not measured field performance. Weight sweeps and scenario counts are not probabilities. No carbon preference until inventory exists."}


def main():
    options,sections=evaluate()
    names={"A":"Drainage-first flexible asphalt","B":"Jointed plain concrete","C":"Targeted asphalt + concrete portfolio"}
    for key,o in options.items():
        o.update(id=key,name=names[key])
        o["project_10km"]={field:value*PROJECT_KM for field,value in o.items() if isinstance(value,(int,float))}
    sensitivity=[]
    for discount,stress_share,stress_overlay,asphalt_factor,concrete_factor in itertools.product(
            [.03,.05,.08],[0,.3,.6],[4,6,8],[.8,1,1.2],[.8,1,1.2]):
        outcome,_=evaluate(discount,stress_share,stress_overlay,8,asphalt_factor,concrete_factor)
        costs={k:v["agency_lcc_npr"] for k,v in outcome.items()}
        best=min(costs.values())
        winners=[key for key,value in costs.items() if abs(value-best)<.01]
        sensitivity.append(dict(discount_rate=discount,stress_share=stress_share,stress_overlay_years=stress_overlay,
                                asphalt_factor=asphalt_factor,concrete_factor=concrete_factor,
                                agency_lcc_npr=costs,winners=winners))
    # Stressed-location advantage at each resurfacing interval, all other assumptions held.
    breakpoints=[]
    for interval in range(3,13):
        _,s=evaluate(stress_overlay=interval)
        a=s["asphalt_stressed"]["agency_lcc_npr"]
        b=s["concrete_stressed"]["agency_lcc_npr"]
        breakpoints.append(dict(asphalt_overlay_years=interval,asphalt_lcc_npr=a,concrete_lcc_npr=b,
                                concrete_minus_asphalt_npr=b-a))
    # Cumulative cash crossings; a temporary crossing isn't a guaranteed payback.
    crossings={}
    for key in ["B","C"]:
        differences=[options[key]["cashflows"][y]["cumulative_discounted_npr"]-options["A"]["cashflows"][y]["cumulative_discounted_npr"] for y in range(31)]
        below=[y for y,d in enumerate(differences) if d<=0]
        sustained=next((y for y in range(31) if all(d<=0 for d in differences[y:])),None)
        crossings[key]={"first_year_at_or_below_A":min(below) if below else None,
                        "first_year_remaining_below_A_to_horizon":sustained,
                        "differences_npr":differences}
    results={
        "metadata":{"title":"Nepal pavement screening model","version":"1.1","analysis_date":"2026-10-18",
                    "price_basis":"Illustrative constant NPR at analysis date; not market-verified estimates",
                    "functional_unit":"1 km of 7 m carriageway; common 1.5 m total shoulder width outside carriageway",
                    "scope":"Reconstruction on an existing, stable, accessible alignment; no land, major earthworks, major structures or utility relocation",
                    "horizon_years":HORIZON,"discount_rate_real":DISCOUNT,"stress_share":STRESS_SHARE,
                    "project_km":PROJECT_KM,"currency":"NPR","npr_per_crore":10000000,
                    "structural_status":"Illustrative section quantities only. No traffic, CBR, fatigue, drainage or flexural design performed.",
                    "lcc_boundary":"Agency direct construction + design/supervision + maintenance - residual credit. Excludes VAT, contingency, user delay, vehicle operating cost and emissions. Not a full economic appraisal.",
                    "residual_policy":"Common assets, pavement structure and localized slab repairs assumed consumed by year30. Remaining asphalt surfacing service credited pro rata from last renewal, including preparatory work as part of renewal service. No recycling cash credit for either pavement.",
                    "schedule_warning":"All intervention intervals are scenarios, not Nepal field service-life measurements. Concrete does not eliminate drainage, foundation or landslide failures."},
        "assumptions":{"width_m":WIDTH,"area_m2_per_km":AREA,"design_supervision_fraction":DESIGN_SUPERVISION,
                       "contingency_fraction":CONTINGENCY,"vat_fraction":VAT,"parameters":PARAMETERS,
                       "common_items":COMMON,"flexible_items":FLEXIBLE,"concrete_items":CONCRETE},
        "options":options,"sections":sections,"selection_matrix":matrix(options),
        "construction_productivity":{
            "status":"Illustrative resource planning, not a contractor programme. Productive days exclude monsoon, breakdowns, approvals, preparation, haul constraints and curing.",
            "asphalt_density_t_per_m3":2.35,"asphalt_placed_t_per_productive_day":500,
            "concrete_placed_m3_per_productive_day":150,
            "drain_crews":4,"drain_metres_per_crew_productive_day":50,
            "project_10km":{
                "A":{"asphalt_t":AREA*PROJECT_KM*.10*2.35,"asphalt_productive_days":AREA*PROJECT_KM*.10*2.35/500},
                "B":{"slab_concrete_m3":AREA*PROJECT_KM*.25,"slab_productive_days":AREA*PROJECT_KM*.25/150},
                "C":{"asphalt_t":AREA*PROJECT_KM*.10*2.35*.7,"asphalt_productive_days":AREA*PROJECT_KM*.10*2.35*.7/500,
                     "slab_concrete_m3":AREA*PROJECT_KM*.25*.3,"slab_productive_days":AREA*PROJECT_KM*.25*.3/150},
                "common_side_drain_productive_days":2000*PROJECT_KM/(4*50)},
            "closure_note":"For new DoR concrete pavement, require minimum28-day traffic closure after slab placement and at least7 days from DLC to slab; detailed engineer-reviewed programme governs."},
        "sensitivity":{"grid":sensitivity,"grid_cases":len(sensitivity),
                       "unique_winner_counts":{k:sum(s["winners"]==[k] for s in sensitivity) for k in options},
                       "tied_cases":sum(len(s["winners"])>1 for s in sensitivity),
                       "interpretation":"Deterministic grid, not a probability distribution; many scenarios deliberately include zero stressed share, where A and C coincide.",
                       "stressed_overlay_breakpoints":breakpoints,"discounted_crossings":crossings,
                       "zero_residual_credit_lcc_npr":{k:o["agency_lcc_npr"]+o["cashflows"][30]["residual_credit_npr"]/(1+DISCOUNT)**30 for k,o in options.items()}},
        "sources":[
            {"id":"DOR-FLEX","title":"DoR Flexible Pavement Design Guideline,2021","url":"https://dor.gov.np/qrdc/publication/qrdc-guidelines-standard-specifications-codes-and-norms/guidelines-for-the-design-of-flexible-pavement-2-21","use":"Site-specific design framework, not source for model layer thicknesses or prices."},
            {"id":"DOR-RIGID","title":"DoR Rigid Pavement Guideline,2021","url":"https://dor.gov.np/qrdc/publication/guidelines-and-manualsguidelines-and-manuals/rigid-pavement-guideline-2-21","use":"Concrete pavement design and joint requirements; model is not a completed design."},
            {"id":"DOR-NORMS","title":"DoR norms for rate analysis,2075; amendment notice2081","url":"https://www.dor.gov.np/qrdc/notice/norms-for-rate-analysis-of-road-and-bridge-works-2075","use":"Required local estimate preparation route. No composite rates copied into this model."},
            {"id":"KTM-RATES","title":"Kathmandu district approved material and wage rates2083/84","url":"https://daokathmandu.moha.gov.np/post/ka-thama-da-ja-l-l-ka-ja-ya-l-thara-tatha-na-ra-ma-nae-sa-maga-ra-ka-sa-va-ka-ta","use":"Verified current schedule exists; scanned PDF not used to claim installed construction prices."},
            {"id":"IRD-VAT","title":"Nepal Inland Revenue Department FAQ","url":"https://ird.gov.np/faq/","use":"13% VAT assumption; application on a particular contract requires estimate verification."},
            {"id":"FHWA-LCCA","title":"FHWA Improving Transportation Investment Decisions Through Life-Cycle Cost Analysis","url":"https://www.fhwa.dot.gov/pavement/lcca/lccafact/","use":"Common service objective, agency costs, timing, discounting, sensitivity. US discount rates not transplanted into Nepal."},
            {"id":"FHWA-RESIDUAL","title":"FHWA Sustainable Pavement Systems,Chapter10","url":"https://www.fhwa.dot.gov/pavement/sustainability/hif15002/chapters/hif15002_10.pdf","use":"Distinguish remaining service value from material salvage. 5% real is analyst scenario, not prescribed rate."},
        ]
    }
    # Meaningful accounting invariants, not a pavement performance validation.
    for key,o in options.items():
        assert abs(sum(r["discounted_npr"] for r in o["cashflows"])-o["agency_lcc_npr"])<.01
        assert abs(o["capex_base_npr"]+o["contingency_npr"]+o["vat_npr"]-o["cash_budget_npr"])<.01
    zero,_=evaluate(stress_share=0)
    assert abs(zero["A"]["agency_lcc_npr"]-zero["C"]["agency_lcc_npr"])<.01
    full,_=evaluate(stress_share=1)
    assert abs(full["B"]["agency_lcc_npr"]-full["C"]["agency_lcc_npr"])<.01
    assert sum(c["weight"] for c in results["selection_matrix"]["criteria"])==100
    (ROOT/"results.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    with (ROOT/"quantities_and_rates.csv").open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=["group"]+list(COMMON[0]));writer.writeheader()
        for group,items in [("common",COMMON),("flexible",FLEXIBLE),("concrete",CONCRETE)]:
            writer.writerows({"group":group,**i} for i in items)
    with (ROOT/"cashflows.csv").open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=["option"]+list(options["A"]["cashflows"][0]));writer.writeheader()
        for key,o in options.items():writer.writerows({"option":key,**r} for r in o["cashflows"])
    with (ROOT/"sensitivity.csv").open("w",newline="",encoding="utf-8-sig") as f:
        fields=["discount_rate","stress_share","stress_overlay_years","asphalt_factor","concrete_factor","A_lcc_npr","B_lcc_npr","C_lcc_npr","winners"]
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for s in sensitivity:
            row={k:s[k] for k in fields[:5]}
            row.update({k+"_lcc_npr":v for k,v in s["agency_lcc_npr"].items()})
            row["winners"]="/".join(s["winners"]);writer.writerow(row)
    with (ROOT/"selection_matrix.csv").open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=["criterion","weight","A","B","C","reason"]);writer.writeheader()
        for c in results["selection_matrix"]["criteria"]:
            writer.writerow({"criterion":c["name"],"weight":c["weight"],**c["scores"],"reason":c["reason"]})
    print(json.dumps({"options":{k:{f:round(o[f]/1e6,3) for f in ["direct_works_npr","capex_base_npr","cash_budget_npr","agency_lcc_npr"]} for k,o in options.items()},
                      "matrix_profiles":results["selection_matrix"]["profiles"],"sensitivity_counts":results["sensitivity"]["unique_winner_counts"],
                      "breakpoints":breakpoints,"crossings":{k:{f:v for f,v in d.items() if f!="differences_npr"} for k,d in crossings.items()}},indent=2))


if __name__=="__main__":
    main()
