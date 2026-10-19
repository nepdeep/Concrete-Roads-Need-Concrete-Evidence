/* Browser counterpart of pavement_model.py. No network/dependencies.
 * Inputs, maintenance events and limitations are documented in results.json.
 * Run the Python script to reproduce the reference JSON and audit tables.
 */
export function evaluatePavements({discountRate=.05,stressShare=.30,stressOverlay=4,
  ordinaryOverlay=8,asphaltFactor=1,concreteFactor=1}={}) {
  if(![discountRate,stressShare,stressOverlay,ordinaryOverlay,asphaltFactor,concreteFactor].every(Number.isFinite)
    ||discountRate<0||discountRate>.25||stressShare<0||stressShare>1
    ||!Number.isInteger(stressOverlay)||stressOverlay<1||stressOverlay>30
    ||!Number.isInteger(ordinaryOverlay)||ordinaryOverlay<1||ordinaryOverlay>30
    ||asphaltFactor<=0||concreteFactor<=0)throw new RangeError('Inputs outside screening model bounds');
  const common=14100000, flexible=19460000, concrete=37940000;
  function section(kind,stressed) {
    const factor=kind==='asphalt'?asphaltFactor:concreteFactor;
    const direct=common+(kind==='asphalt'?flexible:concrete)*factor;
    const capex=direct*1.05;
    let cumulative=0;
    const cashflows=Array.from({length:31},(_,year)=>({year,construction_npr:year===0?capex:0,
      routine_npr:year?180000+(kind==='asphalt'?(stressed?300000:150000):(stressed?150000:80000))*factor:0,
      periodic_npr:0,residual_credit_npr:0}));
    if(kind==='asphalt') {
      const interval=Math.round(stressed?stressOverlay:ordinaryOverlay), cost=7250000*factor;
      let last=0;
      for(let y=interval;y<30;y+=interval){cashflows[y].periodic_npr+=cost;last=y;}
      cashflows[30].residual_credit_npr=(last?cost:6160000*factor)*Math.max(0,interval-(30-last))/interval;
    } else {
      for(const y of [5,10,15,20,25])cashflows[y].periodic_npr+=260000*factor;
      for(const y of [15,25])cashflows[y].periodic_npr+=7000*(stressed?.05:.03)*5500*factor;
    }
    for(const f of cashflows){f.net_npr=f.construction_npr+f.routine_npr+f.periodic_npr-f.residual_credit_npr;
      f.discounted_npr=f.net_npr/(1+discountRate)**f.year;cumulative+=f.discounted_npr;f.cumulative_discounted_npr=cumulative;}
    return {direct_works_npr:direct,capex_base_npr:capex,cashflows,agency_lcc_npr:cumulative};
  }
  function blend(parts,transition=0){
    const direct=parts.reduce((s,[w,p])=>s+w*p.direct_works_npr,0)+transition;
    const capex=direct*1.05,contingency=capex*.15,vat=(capex+contingency)*.13;
    const cashflows=Array.from({length:31},(_,year)=>{
      const f={year};
      for(const key of ['construction_npr','routine_npr','periodic_npr','residual_credit_npr','net_npr','discounted_npr','cumulative_discounted_npr'])
        f[key]=parts.reduce((s,[w,p])=>s+w*p.cashflows[year][key],0);
      if(transition){if(year===0)for(const key of ['construction_npr','net_npr','discounted_npr'])f[key]+=transition*1.05;
        f.cumulative_discounted_npr+=transition*1.05;}
      return f;
    });
    return {direct_works_npr:direct,design_supervision_npr:direct*.05,capex_base_npr:capex,
      contingency_npr:contingency,vat_npr:vat,cash_budget_npr:capex+contingency+vat,
      agency_lcc_npr:cashflows[30].cumulative_discounted_npr,cashflows};
  }
  const p=stressShare,ao=section('asphalt',false),as=section('asphalt',true),co=section('concrete',false),cs=section('concrete',true);
  return {A:blend([[1-p,ao],[p,as]]),B:blend([[1-p,co],[p,cs]]),C:blend([[1-p,ao],[p,cs]],p>0&&p<1?150000:0)};
}
