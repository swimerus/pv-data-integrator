DROP TABLE IF EXISTS pv_source;
DROP SEQUENCE IF EXISTS pv_source_id_seq;
CREATE SEQUENCE pv_source_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE pv_source (
    id integer DEFAULT nextval('pv_source_id_seq') NOT NULL,
    source character varying(15) NOT NULL,
    collect_time timestamp NOT NULL,
    fs_station_code character varying(30),
    creation_date timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT pv_source_id PRIMARY KEY (id)
) WITH (oids = false);

CREATE INDEX pv_source_source ON pv_source USING btree (source);

DROP TABLE IF EXISTS energa_data;
DROP SEQUENCE IF EXISTS energa_data_id_seq;
CREATE SEQUENCE energa_data_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE energa_data (
    id integer DEFAULT nextval('energa_data_id_seq') NOT NULL,
    source_id integer NOT NULL,
    time timestamp NOT NULL,
    energy_type character varying(10),
    zone_1 numeric(6,3) NOT NULL,
    zone_2 numeric(6,3),
    zone_3 numeric(6,3),
    creation_date timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT energa_data_id PRIMARY KEY (id)
) WITH (oids = false);

ALTER TABLE ONLY energa_data ADD CONSTRAINT energa_data_source_id_fkey FOREIGN KEY (source_id) REFERENCES pv_source(id) ON DELETE RESTRICT NOT DEFERRABLE;

DROP TABLE IF EXISTS fusion_solar_data;
DROP SEQUENCE IF EXISTS fusion_solar_data_id_seq;
CREATE SEQUENCE fusion_solar_data_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE fusion_solar_data (
    id integer DEFAULT nextval('fusion_solar_data_id_seq') NOT NULL,
    source_id integer NOT NULL,
    time timestamp NOT NULL,
    inverter_power numeric(6,3) NOT NULL,
    power_profit numeric(6,3) NOT NULL,
    creation_date timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fusion_solar_data_id PRIMARY KEY (id)
) WITH (oids = false);

ALTER TABLE ONLY fusion_solar_data ADD CONSTRAINT fusion_solar_data_source_id_fkey FOREIGN KEY (source_id) REFERENCES pv_source(id) ON DELETE RESTRICT NOT DEFERRABLE;
