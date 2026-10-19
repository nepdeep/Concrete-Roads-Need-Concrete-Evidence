// Verify the web calculation and Python reference agree, including all scenarios.
import {readFileSync} from 'node:fs';
import {evaluatePavements} from './pavement_model.js';
const reference=JSON.parse(readFileSync(new URL('./results.json',import.meta.url),'utf8'));
let assertions=0;
function same(actual,expected,label){assertions++;if(Math.abs(actual-expected)>.01)throw new Error(`${label}: ${actual} != ${expected}`);}
const baseline=evaluatePavements();
for(const key of ['A','B','C']){
  for(const field of ['direct_works_npr','capex_base_npr','cash_budget_npr','agency_lcc_npr'])same(baseline[key][field],reference.options[key][field],`${key}.${field}`);
  for(let year=0;year<=30;year++)same(baseline[key].cashflows[year].cumulative_discounted_npr,
    reference.options[key].cashflows[year].cumulative_discounted_npr,`${key}.year${year}`);
}
for(const s of reference.sensitivity.grid){
  const actual=evaluatePavements({discountRate:s.discount_rate,stressShare:s.stress_share,
    stressOverlay:s.stress_overlay_years,asphaltFactor:s.asphalt_factor,concreteFactor:s.concrete_factor});
  for(const key of ['A','B','C'])same(actual[key].agency_lcc_npr,s.agency_lcc_npr[key],`scenario.${key}`);
}
console.log(`Passed ${assertions} accounting/parity checks across baseline and ${reference.sensitivity.grid.length} scenarios. This does not validate engineering assumptions.`);
