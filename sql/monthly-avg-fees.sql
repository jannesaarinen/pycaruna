select 
	date_part('year', timestamp) as year,
	date_part('month', timestamp) as month,
	count(*),
	round(sum("totalConsumption") :: numeric, 1) as "tottotalConsumptionalFee",
	round(sum("totalFee") :: numeric, 2) as "totalFee",
	round(avg("totalUnitFee"), 4) as "totalUnitFee",
	round(avg("distributionUnitFee"), 4) as "distributionUnitFee",
	round(avg("electricityTaxUnitFee"), 4) as "electricityTaxUnitFee",
	max("valueAddedTaxPct") as "valueAddedTaxPct"
from carunaplus_energy_hourly_unit
group by
	date_part('year', timestamp),
	date_part('month', timestamp)
having
	avg("totalUnitFee") > 0
order by
	month
