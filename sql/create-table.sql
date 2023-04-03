-- Table: public.carunaplus_energy_hourly

-- DROP TABLE IF EXISTS public.carunaplus_energy_hourly;

CREATE TABLE IF NOT EXISTS public.carunaplus_energy_hourly
(
    "timestamp" timestamp with time zone NOT NULL,
    "totalConsumption" double precision,
    "invoicedConsumption" double precision,
    "totalFee" double precision,
    "distributionFee" double precision,
    "distributionBaseFee" double precision,
    "electricityTax" double precision,
    "valueAddedTax" double precision,
    temperature double precision,
    "invoicedConsumptionByTransferProductParts" jsonb,
    "distributionFeeByTransferProductParts" jsonb,
    CONSTRAINT carunaplus_energy_hourly_pkey PRIMARY KEY ("timestamp")
)