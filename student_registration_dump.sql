--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.0
-- Dumped by pg_dump version 9.5.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: hstore; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS hstore WITH SCHEMA public;


--
-- Name: EXTENSION hstore; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION hstore IS 'data type for storing sets of (key, value) pairs';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry, geography, and raster spatial types and functions';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: account_emailaddress; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE account_emailaddress (
    id integer NOT NULL,
    email character varying(254) NOT NULL,
    verified boolean NOT NULL,
    "primary" boolean NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE account_emailaddress OWNER TO postgres;

--
-- Name: account_emailaddress_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE account_emailaddress_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE account_emailaddress_id_seq OWNER TO postgres;

--
-- Name: account_emailaddress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE account_emailaddress_id_seq OWNED BY account_emailaddress.id;


--
-- Name: account_emailconfirmation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE account_emailconfirmation (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    sent timestamp with time zone,
    key character varying(64) NOT NULL,
    email_address_id integer NOT NULL
);


ALTER TABLE account_emailconfirmation OWNER TO postgres;

--
-- Name: account_emailconfirmation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE account_emailconfirmation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE account_emailconfirmation_id_seq OWNER TO postgres;

--
-- Name: account_emailconfirmation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE account_emailconfirmation_id_seq OWNED BY account_emailconfirmation.id;


--
-- Name: alp_extracolumn; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE alp_extracolumn (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    name character varying(64),
    label character varying(64),
    owner_id integer
);


ALTER TABLE alp_extracolumn OWNER TO postgres;

--
-- Name: alp_extracolumn_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE alp_extracolumn_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE alp_extracolumn_id_seq OWNER TO postgres;

--
-- Name: alp_extracolumn_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE alp_extracolumn_id_seq OWNED BY alp_extracolumn.id;


--
-- Name: alp_outreach; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE alp_outreach (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    last_education_year character varying(10),
    average_distance character varying(10),
    exam_year character varying(4),
    exam_month character varying(2),
    exam_day character varying(2),
    extra_fields jsonb,
    last_class_level_id integer,
    last_education_level_id integer,
    location_id integer,
    owner_id integer,
    partner_id integer,
    preferred_language_id integer,
    school_id integer,
    student_id integer
);


ALTER TABLE alp_outreach OWNER TO postgres;

--
-- Name: alp_outreach_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE alp_outreach_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE alp_outreach_id_seq OWNER TO postgres;

--
-- Name: alp_outreach_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE alp_outreach_id_seq OWNED BY alp_outreach.id;


--
-- Name: attendances_attendance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE attendances_attendance (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    status boolean NOT NULL,
    attendance_date date,
    validation_status boolean NOT NULL,
    validation_date date,
    classroom_id integer,
    owner_id integer,
    school_id integer,
    student_id integer,
    validation_owner_id integer
);


ALTER TABLE attendances_attendance OWNER TO postgres;

--
-- Name: attendances_attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE attendances_attendance_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE attendances_attendance_id_seq OWNER TO postgres;

--
-- Name: attendances_attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE attendances_attendance_id_seq OWNED BY attendances_attendance.id;


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE auth_group OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_group_id_seq OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE auth_group_permissions OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_group_permissions_id_seq OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE auth_permission OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_permission_id_seq OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: authtoken_token; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE authtoken_token (
    key character varying(40) NOT NULL,
    created timestamp with time zone NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE authtoken_token OWNER TO postgres;

--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE django_admin_log OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_admin_log_id_seq OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE django_content_type OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_content_type_id_seq OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE django_migrations OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_migrations_id_seq OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_migrations_id_seq OWNED BY django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE django_session OWNER TO postgres;

--
-- Name: django_site; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE django_site OWNER TO postgres;

--
-- Name: django_site_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_site_id_seq OWNER TO postgres;

--
-- Name: django_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;


--
-- Name: eav_attribute; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE eav_attribute (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(50) NOT NULL,
    description character varying(256),
    type character varying(20),
    datatype character varying(6) NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    required boolean NOT NULL,
    shared boolean NOT NULL,
    enum_group_id integer,
    owner_id integer,
    site_id integer NOT NULL
);


ALTER TABLE eav_attribute OWNER TO postgres;

--
-- Name: eav_attribute_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE eav_attribute_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE eav_attribute_id_seq OWNER TO postgres;

--
-- Name: eav_attribute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE eav_attribute_id_seq OWNED BY eav_attribute.id;


--
-- Name: eav_enumgroup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE eav_enumgroup (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE eav_enumgroup OWNER TO postgres;

--
-- Name: eav_enumgroup_enums; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE eav_enumgroup_enums (
    id integer NOT NULL,
    enumgroup_id integer NOT NULL,
    enumvalue_id integer NOT NULL
);


ALTER TABLE eav_enumgroup_enums OWNER TO postgres;

--
-- Name: eav_enumgroup_enums_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE eav_enumgroup_enums_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE eav_enumgroup_enums_id_seq OWNER TO postgres;

--
-- Name: eav_enumgroup_enums_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE eav_enumgroup_enums_id_seq OWNED BY eav_enumgroup_enums.id;


--
-- Name: eav_enumgroup_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE eav_enumgroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE eav_enumgroup_id_seq OWNER TO postgres;

--
-- Name: eav_enumgroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE eav_enumgroup_id_seq OWNED BY eav_enumgroup.id;


--
-- Name: eav_enumvalue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE eav_enumvalue (
    id integer NOT NULL,
    value character varying(50) NOT NULL
);


ALTER TABLE eav_enumvalue OWNER TO postgres;

--
-- Name: eav_enumvalue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE eav_enumvalue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE eav_enumvalue_id_seq OWNER TO postgres;

--
-- Name: eav_enumvalue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE eav_enumvalue_id_seq OWNED BY eav_enumvalue.id;


--
-- Name: eav_value; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE eav_value (
    id integer NOT NULL,
    entity_id integer NOT NULL,
    value_text text,
    value_float double precision,
    value_int integer,
    value_date timestamp with time zone,
    value_bool boolean,
    generic_value_id integer,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    attribute_id integer NOT NULL,
    entity_ct_id integer NOT NULL,
    generic_value_ct_id integer,
    value_enum_id integer
);


ALTER TABLE eav_value OWNER TO postgres;

--
-- Name: eav_value_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE eav_value_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE eav_value_id_seq OWNER TO postgres;

--
-- Name: eav_value_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE eav_value_id_seq OWNED BY eav_value.id;


--
-- Name: locations_location; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE locations_location (
    id integer NOT NULL,
    name character varying(254) NOT NULL,
    latitude double precision,
    longitude double precision,
    p_code character varying(32),
    lft integer NOT NULL,
    rght integer NOT NULL,
    tree_id integer NOT NULL,
    level integer NOT NULL,
    gateway_id integer NOT NULL,
    parent_id integer,
    CONSTRAINT locations_location_level_check CHECK ((level >= 0)),
    CONSTRAINT locations_location_lft_check CHECK ((lft >= 0)),
    CONSTRAINT locations_location_rght_check CHECK ((rght >= 0)),
    CONSTRAINT locations_location_tree_id_check CHECK ((tree_id >= 0))
);


ALTER TABLE locations_location OWNER TO postgres;

--
-- Name: locations_location_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE locations_location_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE locations_location_id_seq OWNER TO postgres;

--
-- Name: locations_location_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE locations_location_id_seq OWNED BY locations_location.id;


--
-- Name: locations_locationtype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE locations_locationtype (
    id integer NOT NULL,
    name character varying(64) NOT NULL
);


ALTER TABLE locations_locationtype OWNER TO postgres;

--
-- Name: locations_locationtype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE locations_locationtype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE locations_locationtype_id_seq OWNER TO postgres;

--
-- Name: locations_locationtype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE locations_locationtype_id_seq OWNED BY locations_locationtype.id;


--
-- Name: registrations_phone; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE registrations_phone (
    id integer NOT NULL,
    prefix character varying(45) NOT NULL,
    number character varying(45) NOT NULL,
    extension character varying(45) NOT NULL,
    type character varying(20),
    adult_id integer NOT NULL
);


ALTER TABLE registrations_phone OWNER TO postgres;

--
-- Name: registrations_phone_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE registrations_phone_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE registrations_phone_id_seq OWNER TO postgres;

--
-- Name: registrations_phone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE registrations_phone_id_seq OWNED BY registrations_phone.id;


--
-- Name: registrations_registeringadult; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE registrations_registeringadult (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    first_name character varying(64),
    last_name character varying(64),
    father_name character varying(64),
    full_name character varying(225),
    mother_fullname character varying(64),
    mother_firstname character varying(64),
    mother_lastname character varying(64),
    sex character varying(50),
    birthday_year character varying(4),
    birthday_month character varying(2),
    birthday_day character varying(2),
    age character varying(4),
    phone character varying(64),
    id_number character varying(45),
    address text,
    number character varying(45),
    status character varying(50),
    previously_registered boolean NOT NULL,
    relation_to_child character varying(50) NOT NULL,
    wfp_case_number character varying(50),
    csc_case_number character varying(50),
    card_issue_requested boolean NOT NULL,
    child_enrolled_in_this_school integer NOT NULL,
    child_enrolled_in_other_schools integer NOT NULL,
    id_type_id integer,
    nationality_id integer,
    school_id integer,
    CONSTRAINT registrations_registeringadu_child_enrolled_in_other_scho_check CHECK ((child_enrolled_in_other_schools >= 0)),
    CONSTRAINT registrations_registeringadu_child_enrolled_in_this_schoo_check CHECK ((child_enrolled_in_this_school >= 0))
);


ALTER TABLE registrations_registeringadult OWNER TO postgres;

--
-- Name: registrations_registeringadult_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE registrations_registeringadult_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE registrations_registeringadult_id_seq OWNER TO postgres;

--
-- Name: registrations_registeringadult_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE registrations_registeringadult_id_seq OWNED BY registrations_registeringadult.id;


--
-- Name: registrations_registration; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE registrations_registration (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    year character varying(4),
    classroom_id integer,
    grade_id integer,
    owner_id integer,
    school_id integer,
    section_id integer,
    student_id integer,
    enrolled_last_year character varying(50),
    relation_to_adult character varying(50),
    registering_adult_id integer
);


ALTER TABLE registrations_registration OWNER TO postgres;

--
-- Name: registrations_registration_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE registrations_registration_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE registrations_registration_id_seq OWNER TO postgres;

--
-- Name: registrations_registration_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE registrations_registration_id_seq OWNED BY registrations_registration.id;


--
-- Name: schools_classlevel; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE schools_classlevel (
    id integer NOT NULL,
    name character varying(45) NOT NULL
);


ALTER TABLE schools_classlevel OWNER TO postgres;

--
-- Name: schools_classlevel_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE schools_classlevel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE schools_classlevel_id_seq OWNER TO postgres;

--
-- Name: schools_classlevel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE schools_classlevel_id_seq OWNED BY schools_classlevel.id;


--
-- Name: schools_classroom; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE schools_classroom (
    id integer NOT NULL,
    name character varying(45) NOT NULL,
    grade_id integer,
    school_id integer,
    section_id integer
);


ALTER TABLE schools_classroom OWNER TO postgres;

--
-- Name: schools_classroom_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE schools_classroom_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE schools_classroom_id_seq OWNER TO postgres;

--
-- Name: schools_classroom_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE schools_classroom_id_seq OWNED BY schools_classroom.id;


--
-- Name: schools_course; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE schools_course (
    id integer NOT NULL,
    name character varying(45) NOT NULL
);


ALTER TABLE schools_course OWNER TO postgres;

--
-- Name: schools_course_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE schools_course_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE schools_course_id_seq OWNER TO postgres;

--
-- Name: schools_course_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE schools_course_id_seq OWNED BY schools_course.id;


--
-- Name: schools_educationlevel; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE schools_educationlevel (
    id integer NOT NULL,
    name character varying(45) NOT NULL
);


ALTER TABLE schools_educationlevel OWNER TO postgres;

--
-- Name: schools_educationlevel_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE schools_educationlevel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE schools_educationlevel_id_seq OWNER TO postgres;

--
-- Name: schools_educationlevel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE schools_educationlevel_id_seq OWNED BY schools_educationlevel.id;


--
-- Name: schools_grade; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE schools_grade (
    id integer NOT NULL,
    name character varying(45) NOT NULL
);


ALTER TABLE schools_grade OWNER TO postgres;

--
-- Name: schools_grade_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE schools_grade_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE schools_grade_id_seq OWNER TO postgres;

--
-- Name: schools_grade_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE schools_grade_id_seq OWNED BY schools_grade.id;


--
-- Name: schools_partnerorganization; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE schools_partnerorganization (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE schools_partnerorganization OWNER TO postgres;

--
-- Name: schools_partnerorganization_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE schools_partnerorganization_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE schools_partnerorganization_id_seq OWNER TO postgres;

--
-- Name: schools_partnerorganization_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE schools_partnerorganization_id_seq OWNED BY schools_partnerorganization.id;


--
-- Name: schools_school; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE schools_school (
    id integer NOT NULL,
    name character varying(555) NOT NULL,
    number character varying(45) NOT NULL,
    location_id integer
);


ALTER TABLE schools_school OWNER TO postgres;

--
-- Name: schools_school_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE schools_school_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE schools_school_id_seq OWNER TO postgres;

--
-- Name: schools_school_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE schools_school_id_seq OWNED BY schools_school.id;


--
-- Name: schools_section; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE schools_section (
    id integer NOT NULL,
    name character varying(45) NOT NULL
);


ALTER TABLE schools_section OWNER TO postgres;

--
-- Name: schools_section_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE schools_section_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE schools_section_id_seq OWNER TO postgres;

--
-- Name: schools_section_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE schools_section_id_seq OWNED BY schools_section.id;


--
-- Name: socialaccount_socialaccount; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE socialaccount_socialaccount (
    id integer NOT NULL,
    provider character varying(30) NOT NULL,
    uid character varying(191) NOT NULL,
    last_login timestamp with time zone NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    extra_data text NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE socialaccount_socialaccount OWNER TO postgres;

--
-- Name: socialaccount_socialaccount_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE socialaccount_socialaccount_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE socialaccount_socialaccount_id_seq OWNER TO postgres;

--
-- Name: socialaccount_socialaccount_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE socialaccount_socialaccount_id_seq OWNED BY socialaccount_socialaccount.id;


--
-- Name: socialaccount_socialapp; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE socialaccount_socialapp (
    id integer NOT NULL,
    provider character varying(30) NOT NULL,
    name character varying(40) NOT NULL,
    client_id character varying(191) NOT NULL,
    secret character varying(191) NOT NULL,
    key character varying(191) NOT NULL
);


ALTER TABLE socialaccount_socialapp OWNER TO postgres;

--
-- Name: socialaccount_socialapp_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE socialaccount_socialapp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE socialaccount_socialapp_id_seq OWNER TO postgres;

--
-- Name: socialaccount_socialapp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE socialaccount_socialapp_id_seq OWNED BY socialaccount_socialapp.id;


--
-- Name: socialaccount_socialapp_sites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE socialaccount_socialapp_sites (
    id integer NOT NULL,
    socialapp_id integer NOT NULL,
    site_id integer NOT NULL
);


ALTER TABLE socialaccount_socialapp_sites OWNER TO postgres;

--
-- Name: socialaccount_socialapp_sites_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE socialaccount_socialapp_sites_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE socialaccount_socialapp_sites_id_seq OWNER TO postgres;

--
-- Name: socialaccount_socialapp_sites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE socialaccount_socialapp_sites_id_seq OWNED BY socialaccount_socialapp_sites.id;


--
-- Name: socialaccount_socialtoken; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE socialaccount_socialtoken (
    id integer NOT NULL,
    token text NOT NULL,
    token_secret text NOT NULL,
    expires_at timestamp with time zone,
    account_id integer NOT NULL,
    app_id integer NOT NULL
);


ALTER TABLE socialaccount_socialtoken OWNER TO postgres;

--
-- Name: socialaccount_socialtoken_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE socialaccount_socialtoken_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE socialaccount_socialtoken_id_seq OWNER TO postgres;

--
-- Name: socialaccount_socialtoken_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE socialaccount_socialtoken_id_seq OWNED BY socialaccount_socialtoken.id;


--
-- Name: students_idtype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE students_idtype (
    id integer NOT NULL,
    name character varying(45) NOT NULL
);


ALTER TABLE students_idtype OWNER TO postgres;

--
-- Name: students_idtype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE students_idtype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE students_idtype_id_seq OWNER TO postgres;

--
-- Name: students_idtype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE students_idtype_id_seq OWNED BY students_idtype.id;


--
-- Name: students_language; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE students_language (
    id integer NOT NULL,
    name character varying(45) NOT NULL
);


ALTER TABLE students_language OWNER TO postgres;

--
-- Name: students_language_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE students_language_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE students_language_id_seq OWNER TO postgres;

--
-- Name: students_language_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE students_language_id_seq OWNED BY students_language.id;


--
-- Name: students_nationality; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE students_nationality (
    id integer NOT NULL,
    name character varying(45) NOT NULL
);


ALTER TABLE students_nationality OWNER TO postgres;

--
-- Name: students_nationality_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE students_nationality_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE students_nationality_id_seq OWNER TO postgres;

--
-- Name: students_nationality_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE students_nationality_id_seq OWNED BY students_nationality.id;


--
-- Name: students_student; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE students_student (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    first_name character varying(64),
    last_name character varying(64),
    father_name character varying(64),
    full_name character varying(225),
    mother_fullname character varying(64),
    sex character varying(50),
    birthday_year character varying(4),
    birthday_month character varying(2),
    birthday_day character varying(2),
    phone character varying(64),
    id_number character varying(45),
    address text,
    nationality_id integer,
    id_type_id integer,
    mother_firstname character varying(64),
    mother_lastname character varying(64),
    number character varying(45),
    age character varying(4)
);


ALTER TABLE students_student OWNER TO postgres;

--
-- Name: students_student_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE students_student_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE students_student_id_seq OWNER TO postgres;

--
-- Name: students_student_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE students_student_id_seq OWNED BY students_student.id;


--
-- Name: users_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE users_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(30) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    phone_number character varying(20),
    partner_id integer,
    school_id integer,
    location_id integer
);


ALTER TABLE users_user OWNER TO postgres;

--
-- Name: users_user_groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE users_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE users_user_groups OWNER TO postgres;

--
-- Name: users_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE users_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE users_user_groups_id_seq OWNER TO postgres;

--
-- Name: users_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE users_user_groups_id_seq OWNED BY users_user_groups.id;


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE users_user_id_seq OWNED BY users_user.id;


--
-- Name: users_user_user_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE users_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE users_user_user_permissions OWNER TO postgres;

--
-- Name: users_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE users_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE users_user_user_permissions_id_seq OWNER TO postgres;

--
-- Name: users_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE users_user_user_permissions_id_seq OWNED BY users_user_user_permissions.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_emailaddress ALTER COLUMN id SET DEFAULT nextval('account_emailaddress_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_emailconfirmation ALTER COLUMN id SET DEFAULT nextval('account_emailconfirmation_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_extracolumn ALTER COLUMN id SET DEFAULT nextval('alp_extracolumn_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_outreach ALTER COLUMN id SET DEFAULT nextval('alp_outreach_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY attendances_attendance ALTER COLUMN id SET DEFAULT nextval('attendances_attendance_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_migrations ALTER COLUMN id SET DEFAULT nextval('django_migrations_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_attribute ALTER COLUMN id SET DEFAULT nextval('eav_attribute_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_enumgroup ALTER COLUMN id SET DEFAULT nextval('eav_enumgroup_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_enumgroup_enums ALTER COLUMN id SET DEFAULT nextval('eav_enumgroup_enums_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_enumvalue ALTER COLUMN id SET DEFAULT nextval('eav_enumvalue_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_value ALTER COLUMN id SET DEFAULT nextval('eav_value_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY locations_location ALTER COLUMN id SET DEFAULT nextval('locations_location_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY locations_locationtype ALTER COLUMN id SET DEFAULT nextval('locations_locationtype_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_phone ALTER COLUMN id SET DEFAULT nextval('registrations_phone_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registeringadult ALTER COLUMN id SET DEFAULT nextval('registrations_registeringadult_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registration ALTER COLUMN id SET DEFAULT nextval('registrations_registration_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_classlevel ALTER COLUMN id SET DEFAULT nextval('schools_classlevel_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_classroom ALTER COLUMN id SET DEFAULT nextval('schools_classroom_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_course ALTER COLUMN id SET DEFAULT nextval('schools_course_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_educationlevel ALTER COLUMN id SET DEFAULT nextval('schools_educationlevel_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_grade ALTER COLUMN id SET DEFAULT nextval('schools_grade_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_partnerorganization ALTER COLUMN id SET DEFAULT nextval('schools_partnerorganization_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_school ALTER COLUMN id SET DEFAULT nextval('schools_school_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_section ALTER COLUMN id SET DEFAULT nextval('schools_section_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialaccount ALTER COLUMN id SET DEFAULT nextval('socialaccount_socialaccount_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialapp ALTER COLUMN id SET DEFAULT nextval('socialaccount_socialapp_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialapp_sites ALTER COLUMN id SET DEFAULT nextval('socialaccount_socialapp_sites_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialtoken ALTER COLUMN id SET DEFAULT nextval('socialaccount_socialtoken_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_idtype ALTER COLUMN id SET DEFAULT nextval('students_idtype_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_language ALTER COLUMN id SET DEFAULT nextval('students_language_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_nationality ALTER COLUMN id SET DEFAULT nextval('students_nationality_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_student ALTER COLUMN id SET DEFAULT nextval('students_student_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user ALTER COLUMN id SET DEFAULT nextval('users_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user_groups ALTER COLUMN id SET DEFAULT nextval('users_user_groups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('users_user_user_permissions_id_seq'::regclass);


--
-- Data for Name: account_emailaddress; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY account_emailaddress (id, email, verified, "primary", user_id) FROM stdin;
1	ali.chamseddine21@gmail.com	t	t	2
2	achamseddine@unicef.org	t	t	1
\.


--
-- Name: account_emailaddress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('account_emailaddress_id_seq', 2, true);


--
-- Data for Name: account_emailconfirmation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY account_emailconfirmation (id, created, sent, key, email_address_id) FROM stdin;
1	2016-08-19 14:05:30.916525+03	2016-08-19 14:05:30.93606+03	sncgyxbf2acw5iabcubkpvyd5sde6kegto2szhbzk9v64zrkigfj95whp5fwtdu5	1
2	2016-08-24 10:58:06.192239+03	2016-08-24 10:58:06.84526+03	p00ynsu2gq2ggnwm7vmdeywhlivcdrbtnggqgbsdix6arkfr7d2qracxbufu2nwd	2
\.


--
-- Name: account_emailconfirmation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('account_emailconfirmation_id_seq', 2, true);


--
-- Data for Name: alp_extracolumn; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY alp_extracolumn (id, created, modified, name, label, owner_id) FROM stdin;
\.


--
-- Name: alp_extracolumn_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('alp_extracolumn_id_seq', 1, false);


--
-- Data for Name: alp_outreach; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY alp_outreach (id, created, modified, last_education_year, average_distance, exam_year, exam_month, exam_day, extra_fields, last_class_level_id, last_education_level_id, location_id, owner_id, partner_id, preferred_language_id, school_id, student_id) FROM stdin;
5	2016-08-23 22:23:01.536564+03	2016-08-23 22:23:01.546918+03	2000/2001	> 10km	1990	3	3	\N	1	1	1	2	1	1	1	5
6	2016-08-25 14:44:58.098878+03	2016-08-25 14:44:58.115121+03	2005/2006	> 10km	1991	2	3	\N	1	1	1	2	1	1	1	6
7	2016-08-25 14:50:59.65088+03	2016-08-25 14:50:59.669835+03	2001/2002	> 10km	1991	4	4	\N	1	1	1	2	1	1	1	7
8	2016-08-26 16:04:22.394148+03	2016-08-26 16:04:22.409924+03	2000/2001	> 10km	1993	3	3	\N	1	1	1	2	1	1	1	8
\.


--
-- Name: alp_outreach_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('alp_outreach_id_seq', 8, true);


--
-- Data for Name: attendances_attendance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY attendances_attendance (id, created, modified, status, attendance_date, validation_status, validation_date, classroom_id, owner_id, school_id, student_id, validation_owner_id) FROM stdin;
\.


--
-- Name: attendances_attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('attendances_attendance_id_seq', 1, false);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_group (id, name) FROM stdin;
1	Member
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_group_id_seq', 1, true);


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
1	1	97
2	1	98
3	1	99
4	1	100
5	1	101
6	1	102
7	1	46
8	1	47
9	1	48
10	1	49
11	1	50
12	1	51
13	1	58
14	1	59
15	1	60
\.


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 15, true);


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add permission	1	add_permission
2	Can change permission	1	change_permission
3	Can delete permission	1	delete_permission
4	Can add group	2	add_group
5	Can change group	2	change_group
6	Can delete group	2	delete_group
7	Can add content type	3	add_contenttype
8	Can change content type	3	change_contenttype
9	Can delete content type	3	delete_contenttype
10	Can add session	4	add_session
11	Can change session	4	change_session
12	Can delete session	4	delete_session
13	Can add site	5	add_site
14	Can change site	5	change_site
15	Can delete site	5	delete_site
16	Can add log entry	6	add_logentry
17	Can change log entry	6	change_logentry
18	Can delete log entry	6	delete_logentry
19	Can add email address	7	add_emailaddress
20	Can change email address	7	change_emailaddress
21	Can delete email address	7	delete_emailaddress
22	Can add email confirmation	8	add_emailconfirmation
23	Can change email confirmation	8	change_emailconfirmation
24	Can delete email confirmation	8	delete_emailconfirmation
25	Can add social application	9	add_socialapp
26	Can change social application	9	change_socialapp
27	Can delete social application	9	delete_socialapp
28	Can add social account	10	add_socialaccount
29	Can change social account	10	change_socialaccount
30	Can delete social account	10	delete_socialaccount
31	Can add social application token	11	add_socialtoken
32	Can change social application token	11	change_socialtoken
33	Can delete social application token	11	delete_socialtoken
34	Can add Token	12	add_token
35	Can change Token	12	change_token
36	Can delete Token	12	delete_token
37	Can add user	13	add_user
38	Can change user	13	change_user
39	Can delete user	13	delete_user
40	Can add nationality	14	add_nationality
41	Can change nationality	14	change_nationality
42	Can delete nationality	14	delete_nationality
43	Can add language	15	add_language
44	Can change language	15	change_language
45	Can delete language	15	delete_language
46	Can add student	16	add_student
47	Can change student	16	change_student
48	Can delete student	16	delete_student
49	Can add outreach	17	add_outreach
50	Can change outreach	17	change_outreach
51	Can delete outreach	17	delete_outreach
52	Can add extra column	18	add_extracolumn
53	Can change extra column	18	change_extracolumn
54	Can delete extra column	18	delete_extracolumn
55	Can add attendance	19	add_attendance
56	Can change attendance	19	change_attendance
57	Can delete attendance	19	delete_attendance
58	Can add registration	20	add_registration
59	Can change registration	20	change_registration
60	Can delete registration	20	delete_registration
61	Can add school	21	add_school
62	Can change school	21	change_school
63	Can delete school	21	delete_school
64	Can add course	22	add_course
65	Can change course	22	change_course
66	Can delete course	22	delete_course
67	Can add education level	23	add_educationlevel
68	Can change education level	23	change_educationlevel
69	Can delete education level	23	delete_educationlevel
70	Can add class level	24	add_classlevel
71	Can change class level	24	change_classlevel
72	Can delete class level	24	delete_classlevel
73	Can add grade	25	add_grade
74	Can change grade	25	change_grade
75	Can delete grade	25	delete_grade
76	Can add section	26	add_section
77	Can change section	26	change_section
78	Can delete section	26	delete_section
79	Can add class room	27	add_classroom
80	Can change class room	27	change_classroom
81	Can delete class room	27	delete_classroom
82	Can add partner organization	28	add_partnerorganization
83	Can change partner organization	28	change_partnerorganization
84	Can delete partner organization	28	delete_partnerorganization
85	Can add Location Type	29	add_locationtype
86	Can change Location Type	29	change_locationtype
87	Can delete Location Type	29	delete_locationtype
88	Can add location	30	add_location
89	Can change location	30	change_location
90	Can delete location	30	delete_location
91	Can add enum value	31	add_enumvalue
92	Can change enum value	31	change_enumvalue
93	Can delete enum value	31	delete_enumvalue
94	Can add enum group	32	add_enumgroup
95	Can change enum group	32	change_enumgroup
96	Can delete enum group	32	delete_enumgroup
97	Can add attribute	33	add_attribute
98	Can change attribute	33	change_attribute
99	Can delete attribute	33	delete_attribute
100	Can add value	34	add_value
101	Can change value	34	change_value
102	Can delete value	34	delete_value
103	Can add id type	35	add_idtype
104	Can change id type	35	change_idtype
105	Can delete id type	35	delete_idtype
106	Can add registering adult	36	add_registeringadult
107	Can change registering adult	36	change_registeringadult
108	Can delete registering adult	36	delete_registeringadult
109	Can add phone	37	add_phone
110	Can change phone	37	change_phone
111	Can delete phone	37	delete_phone
\.


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_permission_id_seq', 111, true);


--
-- Data for Name: authtoken_token; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY authtoken_token (key, created, user_id) FROM stdin;
5c658e9c9670511d7601fa61798832ed286d482d	2016-08-19 23:12:28.281738+03	2
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2016-08-19 11:47:46.310557+03	2	ali.chamseddine	2	Modification de is_superuser et is_staff.	13	1
2	2016-08-19 11:52:22.71087+03	1	Member	1	Ajout.	2	1
3	2016-08-19 11:52:39.637364+03	2	ali.chamseddine	2	Modification de groups.	13	1
4	2016-08-22 20:24:24.768506+03	1	محافظة	1	تمت الإضافة.	29	1
5	2016-08-22 20:24:28.080523+03	1	عكار - محافظة	1	تمت الإضافة.	30	1
6	2016-08-22 20:24:30.253115+03	1	school 1	1	تمت الإضافة.	21	1
7	2016-08-22 20:25:04.133715+03	1	Class  level1	1	تمت الإضافة.	24	1
8	2016-08-22 20:25:17.685165+03	1	Class 1	1	تمت الإضافة.	27	1
9	2016-08-22 20:25:27.905417+03	1	level 1	1	تمت الإضافة.	23	1
10	2016-08-22 20:25:41.874274+03	1	Grade 1	1	تمت الإضافة.	25	1
11	2016-08-22 20:26:00.476786+03	1	Partner 1	1	تمت الإضافة.	28	1
12	2016-08-22 20:26:28.635613+03	1	A	1	تمت الإضافة.	26	1
13	2016-08-22 20:31:48.424252+03	1	type	1	تمت الإضافة.	35	1
14	2016-08-22 20:31:58.555027+03	1	frensh	1	تمت الإضافة.	15	1
15	2016-08-22 20:32:09.682445+03	1	syrien	1	تمت الإضافة.	14	1
16	2016-08-22 20:36:25.556078+03	1	eav1 (نص)	3		33	1
17	2016-08-22 20:36:25.560675+03	2	eav2 (نص)	3		33	1
18	2016-08-22 21:15:18.136732+03	3	fffffffff - eav 1: "eav 1"	2	عدّل entity_id.	34	1
19	2016-08-23 15:43:53.121403+03	3	fffffffff - eav 1: "eav 1"	3		34	1
20	2016-08-23 15:44:04.639158+03	5	eav 1 (Text)	3		33	1
21	2016-08-23 15:44:04.64414+03	3	eav 1 (Text)	3		33	1
22	2016-08-23 15:44:04.648623+03	4	eav2 (Text)	3		33	1
23	2016-08-23 15:44:04.655812+03	6	vfdsvf dd (Text)	3		33	1
24	2016-08-23 22:02:48.146562+03	4	dkjshd jhkshjgdhj - test: "test 1222"	3		34	1
25	2016-08-23 22:02:59.212537+03	7	test (Text)	3		33	1
26	2016-08-23 22:21:15.299633+03	8	test (Text)	3		33	1
27	2016-08-23 22:24:28.542519+03	1	cervrevrvd  ef	3		17	1
28	2016-08-23 22:24:28.547687+03	2	fffffffff	3		17	1
29	2016-08-23 22:24:28.554137+03	3	dkjshd jhkshjgdhj	3		17	1
30	2016-08-25 09:14:15.391376+03	6	ddddd - test 1: "aliiiii"	3		34	1
31	2016-08-25 09:14:20.796156+03	9	test 1 (نص)	2	عدّل slug، shared و owner.	33	1
32	2016-08-25 11:54:49.970831+03	10	test 2 (نص)	1	تمت الإضافة.	33	1
33	2016-08-25 13:58:08.030459+03	10	test 2 (نص)	2	عدّل type.	33	1
34	2016-08-25 21:55:16.173629+03	11	test1 (نص)	3		33	1
35	2016-08-26 12:05:23.110362+03	12	gfdfgsdfds - test 3: ""	3		34	1
36	2016-08-26 12:05:23.118549+03	10	gfdfgsdfds - test 1: "jhghjghjghg"	3		34	1
37	2016-08-26 12:05:23.123004+03	9	gfdfgsdfds - test 2: "hghjgjhghg"	3		34	1
38	2016-08-26 12:05:23.127605+03	8	None - test 2: ""	3		34	1
39	2016-08-26 12:05:23.131971+03	7	None - test 1: ""	3		34	1
40	2016-08-26 12:06:52.083829+03	13	ddddd - test 1: "kjdh vkjshfjkhdjkfh k"	1	تمت الإضافة.	34	1
\.


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 40, true);


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_content_type (id, app_label, model) FROM stdin;
1	auth	permission
2	auth	group
3	contenttypes	contenttype
4	sessions	session
5	sites	site
6	admin	logentry
7	account	emailaddress
8	account	emailconfirmation
9	socialaccount	socialapp
10	socialaccount	socialaccount
11	socialaccount	socialtoken
12	authtoken	token
13	users	user
14	students	nationality
15	students	language
16	students	student
17	alp	outreach
18	alp	extracolumn
19	attendances	attendance
20	registrations	registration
21	schools	school
22	schools	course
23	schools	educationlevel
24	schools	classlevel
25	schools	grade
26	schools	section
27	schools	classroom
28	schools	partnerorganization
29	locations	locationtype
30	locations	location
31	eav	enumvalue
32	eav	enumgroup
33	eav	attribute
34	eav	value
35	students	idtype
36	registrations	registeringadult
37	registrations	phone
\.


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_content_type_id_seq', 37, true);


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_migrations (id, app, name, applied) FROM stdin;
1	locations	0001_initial	2016-08-19 11:44:24.954788+03
2	schools	0001_initial	2016-08-19 11:44:25.051761+03
3	contenttypes	0001_initial	2016-08-19 11:44:25.064945+03
4	contenttypes	0002_remove_content_type_name	2016-08-19 11:44:25.080332+03
5	auth	0001_initial	2016-08-19 11:44:25.122922+03
6	auth	0002_alter_permission_name_max_length	2016-08-19 11:44:25.132487+03
7	auth	0003_alter_user_email_max_length	2016-08-19 11:44:25.141532+03
8	auth	0004_alter_user_username_opts	2016-08-19 11:44:25.151507+03
9	auth	0005_alter_user_last_login_null	2016-08-19 11:44:25.164332+03
10	auth	0006_require_contenttypes_0002	2016-08-19 11:44:25.16661+03
11	auth	0007_alter_validators_add_error_messages	2016-08-19 11:44:25.177682+03
12	users	0001_initial	2016-08-19 11:44:25.227868+03
13	account	0001_initial	2016-08-19 11:44:25.283376+03
14	account	0002_email_max_length	2016-08-19 11:44:25.306632+03
15	admin	0001_initial	2016-08-19 11:44:25.374862+03
16	admin	0002_logentry_remove_auto_add	2016-08-19 11:44:25.399786+03
17	students	0001_initial	2016-08-19 11:44:25.43471+03
18	alp	0001_initial	2016-08-19 11:44:25.478966+03
19	alp	0002_auto_20160819_1142	2016-08-19 11:44:25.660769+03
20	attendances	0001_initial	2016-08-19 11:44:25.700687+03
21	attendances	0002_auto_20160819_1142	2016-08-19 11:44:25.846132+03
22	authtoken	0001_initial	2016-08-19 11:44:25.888527+03
23	authtoken	0002_auto_20160226_1747	2016-08-19 11:44:26.045551+03
24	sites	0001_initial	2016-08-19 11:44:26.054882+03
25	sites	0002_set_site_domain_and_name	2016-08-19 11:44:26.06279+03
26	sites	0003_auto_20160517_1646	2016-08-19 11:44:26.072796+03
27	eav	0001_initial	2016-08-19 11:44:26.248394+03
28	eav	0002_auto_20160819_1142	2016-08-19 11:44:26.387882+03
29	registrations	0001_initial	2016-08-19 11:44:26.445277+03
30	registrations	0002_auto_20160819_1142	2016-08-19 11:44:26.698019+03
31	sessions	0001_initial	2016-08-19 11:44:26.710508+03
32	socialaccount	0001_initial	2016-08-19 11:44:26.970903+03
33	socialaccount	0002_token_max_lengths	2016-08-19 11:44:27.173746+03
34	socialaccount	0003_extra_data_default_dict	2016-08-19 11:44:27.225161+03
35	students	0002_auto_20160820_1422	2016-08-20 14:22:52.506735+03
36	students	0003_auto_20160820_1428	2016-08-20 14:28:33.504849+03
37	users	0002_user_location	2016-08-20 14:28:33.60541+03
38	students	0004_student_number	2016-08-23 22:15:16.651092+03
39	students	0005_student_age	2016-08-27 22:53:05.396361+03
40	registrations	0003_auto_20160827_2252	2016-08-27 22:53:05.868856+03
41	registrations	0004_registration_registering_adult	2016-08-27 22:59:40.729296+03
42	registrations	0005_registeringadult_school	2016-08-30 11:15:21.182713+03
\.


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_migrations_id_seq', 42, true);


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_session (session_key, session_data, expire_date) FROM stdin;
u848hlnfgr9yd4zc5j3z28xghk5adcge	MDZkYjhlMTQ5NTY4ZmUyYzgxN2Q3OGJkYzljMjg3YmM4MTVlMjQ2OTp7Il9sYW5ndWFnZSI6ImFyLWFyIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI3MGQxNzk2YjQyYzBjNDI2Y2NlNmYyMjNkNWM0NWQ1NzYyYjI5ZjFkIiwiX2F1dGhfdXNlcl9pZCI6IjIiLCJfc2Vzc2lvbl9leHBpcnkiOjB9	2016-09-02 14:12:39.148575+03
pgx65b32kh8aoz1bfeu9zgatgubz604a	ODc3ZWIwODI2NWNjOWNiYmIxMjIxYTZlZmNjMjY3YzZmZDllYjlkMzp7Il9sYW5ndWFnZSI6ImVuLXVzIiwiX3Nlc3Npb25fZXhwaXJ5IjowLCJfYXV0aF91c2VyX2hhc2giOiI3MGQxNzk2YjQyYzBjNDI2Y2NlNmYyMjNkNWM0NWQ1NzYyYjI5ZjFkIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMiJ9	2016-09-02 23:13:09.725016+03
10jcoupyf2v6lp0ci24iaanf0m02uozu	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-03 21:08:13.422076+03
8q3l0hyojotl0x5ows33dxzwx619qg0v	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-03 21:09:20.235024+03
j3mupkm6ae1xry8s4nqrz5omm24882hq	MWViNzY1OTMwODI2MjYyMGIwMDg3Nzg3YzM1M2EyMjUyZWE4Yzg0NTp7Il9sYW5ndWFnZSI6ImFyLWFyIiwiX2F1dGhfdXNlcl9pZCI6IjIiLCJfYXV0aF91c2VyX2hhc2giOiI3MGQxNzk2YjQyYzBjNDI2Y2NlNmYyMjNkNWM0NWQ1NzYyYjI5ZjFkIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfc2Vzc2lvbl9leHBpcnkiOjB9	2016-09-04 21:41:22.938127+03
viv3e97n2w1us4e8r5voxdk6gybfdov2	NmM1NzIwNzE1MGI1ZmY1NTZhYjgxNTA4NjcyZmU4YzM1OTExYzEwNTp7Il9sYW5ndWFnZSI6ImFyLWFyIiwiX2F1dGhfdXNlcl9oYXNoIjoiZGY2NzIxNGI0ZTBjNTQ4Yjk5NDk0NDI3NGM2N2Q0YTlmMDZiZjQyMSIsIl9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQifQ==	2016-09-05 12:15:42.160495+03
2foz16ny2rh39it7u6e5zuh0hxxnuynb	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-05 21:05:44.332065+03
6g7609ec8xkk17ybyotetiw070m1z77y	YWYwYjBmNmQyOGVmODM1MGEyOTcwY2FmZGE1NjE2YWVkZTQ3MzMyMjp7Il9hdXRoX3VzZXJfaGFzaCI6ImRmNjcyMTRiNGUwYzU0OGI5OTQ5NDQyNzRjNjdkNGE5ZjA2YmY0MjEiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZCIsIl9hdXRoX3VzZXJfaWQiOiIxIn0=	2016-09-06 15:43:40.295384+03
76vpi71p85lxnombn6wbd1oot9e86jpc	MmM2OTMzZTZmZWJlMGVjMGUxOTZjMGJmMTVhMTkyOTlmZTRlNzg1Yjp7Il9sYW5ndWFnZSI6ImFyLWFyIiwiX3Nlc3Npb25fZXhwaXJ5IjowLCJfYXV0aF91c2VyX2hhc2giOiJkZjY3MjE0YjRlMGM1NDhiOTk0OTQ0Mjc0YzY3ZDRhOWYwNmJmNDIxIiwiX2F1dGhfdXNlcl9pZCI6IjEiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZCJ9	2016-09-07 10:58:40.547236+03
mxagtkf8ytmzadb4bszl7zhzib4vfgyu	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-07 14:40:25.380878+03
0a5hma4ybjrtcf2int8pqxnugq66wcr0	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 10:26:24.631253+03
0z51yj2uwjxr6s0lwy7cnfvssue4p36n	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 10:26:46.901618+03
0jyiwm7f870desycfedjvd0db5q2hcdc	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 11:25:16.056752+03
16gw7cw5dx40e3prc024g8762znt91de	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 11:42:23.36561+03
74vm00j0f6p0odn1yv2603fxp8e9dc3a	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 11:49:56.105585+03
crmr62s8zxi4vdij3lvaoetcr94ha70r	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 11:52:33.530572+03
gnopbuv042kak2j0urtp00fnlup7ibxu	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 11:53:48.528346+03
vz6irgn9e0oj1xu3se9o2e873hcl4mak	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 11:55:55.276884+03
ztfzxv4lpzug0050yxovasbwcmb1tw2o	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 13:13:42.595262+03
pchk31zdgvwuc1r5frv0750xhx9fmlua	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 13:24:55.293801+03
7aawmu6jmc8nl9zx0u3snkfvwc5rbmqp	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 13:27:30.919716+03
fcl1optv2thdhht14l4ch2si0g2ttvim	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 13:28:59.523214+03
qst7zoo77912hbpjkfneqpzqbx4zvhqa	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 13:46:54.270878+03
m83yffsta7e7xzj4tdimdz2kfd6umppi	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-10 23:24:33.812642+03
3j4gigtsix3gwr0n41z81gdozq3ktocl	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 14:13:37.93025+03
brlxdn3rfjcccza9jsnp6wgz6jckqi3m	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-08 14:14:38.02586+03
71tqf0n6r38081b0tkp077kvenattb19	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-11 17:42:02.590002+03
knhaddh7zqyv95yygasarpky8mrjmc9k	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-09 16:10:11.785473+03
dc9sni38h45z9ugh83plkqxkgp43wta0	YmZkNDQ5YzlhZWQzZTAwYzM3MWM0NzQwNTFlNGQwNjMwNDM1ZGE5Yzp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNzBkMTc5NmI0MmMwYzQyNmNjZTZmMjIzZDVjNDVkNTc2MmIyOWYxZCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6IjIifQ==	2016-09-09 16:10:56.164113+03
xoj9fkhcqun6sw8s01p2n9vmawpc2vef	YWYwYjBmNmQyOGVmODM1MGEyOTcwY2FmZGE1NjE2YWVkZTQ3MzMyMjp7Il9hdXRoX3VzZXJfaGFzaCI6ImRmNjcyMTRiNGUwYzU0OGI5OTQ5NDQyNzRjNjdkNGE5ZjA2YmY0MjEiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZCIsIl9hdXRoX3VzZXJfaWQiOiIxIn0=	2016-09-12 19:08:14.429918+03
\.


--
-- Data for Name: django_site; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_site (id, domain, name) FROM stdin;
1	monitoring.uniceflebanon.org	Student Registration
\.


--
-- Name: django_site_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_site_id_seq', 1, false);


--
-- Data for Name: eav_attribute; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY eav_attribute (id, name, slug, description, type, datatype, created, modified, required, shared, enum_group_id, owner_id, site_id) FROM stdin;
9	test 1	extra-column-1-2		outreach	text	2016-08-23 22:25:30.158636+03	2016-08-25 09:14:20.791257+03	f	t	\N	1	1
10	test 2	extra-column-1-3		outreach	text	2016-08-25 11:54:49.913035+03	2016-08-25 13:58:08.025107+03	f	t	\N	1	1
12	test 3	extra-column-2-4	\N	outreach	text	2016-08-25 21:55:54.074255+03	2016-08-25 21:55:54.079724+03	f	f	\N	2	1
13	test 6	extra-column-2-2	\N	outreach	text	2016-08-26 16:02:59.072694+03	2016-08-26 16:02:59.078343+03	f	f	\N	2	1
\.


--
-- Name: eav_attribute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('eav_attribute_id_seq', 13, true);


--
-- Data for Name: eav_enumgroup; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY eav_enumgroup (id, name) FROM stdin;
\.


--
-- Data for Name: eav_enumgroup_enums; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY eav_enumgroup_enums (id, enumgroup_id, enumvalue_id) FROM stdin;
\.


--
-- Name: eav_enumgroup_enums_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('eav_enumgroup_enums_id_seq', 1, false);


--
-- Name: eav_enumgroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('eav_enumgroup_id_seq', 1, false);


--
-- Data for Name: eav_enumvalue; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY eav_enumvalue (id, value) FROM stdin;
\.


--
-- Name: eav_enumvalue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('eav_enumvalue_id_seq', 1, false);


--
-- Data for Name: eav_value; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY eav_value (id, entity_id, value_text, value_float, value_int, value_date, value_bool, generic_value_id, created, modified, attribute_id, entity_ct_id, generic_value_ct_id, value_enum_id) FROM stdin;
13	5	kjdh vkjshfjkhdjkfh k	\N	\N	\N	\N	\N	2016-08-26 12:05:25+03	2016-08-26 12:06:52.068267+03	9	17	\N	\N
14	8	fsfdsdfsfds	\N	\N	\N	\N	\N	2016-08-26 16:04:27.526559+03	2016-08-26 16:04:27.537321+03	10	17	\N	\N
15	8	gfsfdsfds	\N	\N	\N	\N	\N	2016-08-26 16:04:27.51408+03	2016-08-26 16:04:27.542531+03	9	17	\N	\N
16	8		\N	\N	\N	\N	\N	2016-08-26 16:04:27.529836+03	2016-08-26 16:04:27.549277+03	10	17	\N	\N
17	8		\N	\N	\N	\N	\N	2016-08-26 16:04:27.55269+03	2016-08-26 16:04:27.558871+03	9	17	\N	\N
19	8		\N	\N	\N	\N	\N	2016-08-28 00:31:05.666945+03	2016-08-28 00:31:05.670803+03	9	17	\N	\N
20	8		\N	\N	\N	\N	\N	2016-08-28 00:31:05.702419+03	2016-08-28 00:31:05.704979+03	10	17	\N	\N
\.


--
-- Name: eav_value_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('eav_value_id_seq', 20, true);


--
-- Data for Name: locations_location; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY locations_location (id, name, latitude, longitude, p_code, lft, rght, tree_id, level, gateway_id, parent_id) FROM stdin;
1	عكار	\N	\N		1	2	1	0	1	\N
\.


--
-- Name: locations_location_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('locations_location_id_seq', 1, true);


--
-- Data for Name: locations_locationtype; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY locations_locationtype (id, name) FROM stdin;
1	محافظة
\.


--
-- Name: locations_locationtype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('locations_locationtype_id_seq', 1, true);


--
-- Data for Name: registrations_phone; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY registrations_phone (id, prefix, number, extension, type, adult_id) FROM stdin;
\.


--
-- Name: registrations_phone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('registrations_phone_id_seq', 1, false);


--
-- Data for Name: registrations_registeringadult; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY registrations_registeringadult (id, created, modified, first_name, last_name, father_name, full_name, mother_fullname, mother_firstname, mother_lastname, sex, birthday_year, birthday_month, birthday_day, age, phone, id_number, address, number, status, previously_registered, relation_to_child, wfp_case_number, csc_case_number, card_issue_requested, child_enrolled_in_this_school, child_enrolled_in_other_schools, id_type_id, nationality_id, school_id) FROM stdin;
\.


--
-- Name: registrations_registeringadult_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('registrations_registeringadult_id_seq', 1, false);


--
-- Data for Name: registrations_registration; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY registrations_registration (id, created, modified, year, classroom_id, grade_id, owner_id, school_id, section_id, student_id, enrolled_last_year, relation_to_adult, registering_adult_id) FROM stdin;
\.


--
-- Name: registrations_registration_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('registrations_registration_id_seq', 1, false);


--
-- Data for Name: schools_classlevel; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY schools_classlevel (id, name) FROM stdin;
1	Class  level1
\.


--
-- Name: schools_classlevel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('schools_classlevel_id_seq', 1, true);


--
-- Data for Name: schools_classroom; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY schools_classroom (id, name, grade_id, school_id, section_id) FROM stdin;
1	Class 1	\N	\N	\N
\.


--
-- Name: schools_classroom_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('schools_classroom_id_seq', 1, true);


--
-- Data for Name: schools_course; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY schools_course (id, name) FROM stdin;
\.


--
-- Name: schools_course_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('schools_course_id_seq', 1, false);


--
-- Data for Name: schools_educationlevel; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY schools_educationlevel (id, name) FROM stdin;
1	level 1
\.


--
-- Name: schools_educationlevel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('schools_educationlevel_id_seq', 1, true);


--
-- Data for Name: schools_grade; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY schools_grade (id, name) FROM stdin;
1	Grade 1
\.


--
-- Name: schools_grade_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('schools_grade_id_seq', 1, true);


--
-- Data for Name: schools_partnerorganization; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY schools_partnerorganization (id, name) FROM stdin;
1	Partner 1
\.


--
-- Name: schools_partnerorganization_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('schools_partnerorganization_id_seq', 1, true);


--
-- Data for Name: schools_school; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY schools_school (id, name, number, location_id) FROM stdin;
1	school 1	648	1
\.


--
-- Name: schools_school_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('schools_school_id_seq', 1, true);


--
-- Data for Name: schools_section; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY schools_section (id, name) FROM stdin;
1	A
\.


--
-- Name: schools_section_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('schools_section_id_seq', 1, true);


--
-- Data for Name: socialaccount_socialaccount; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY socialaccount_socialaccount (id, provider, uid, last_login, date_joined, extra_data, user_id) FROM stdin;
\.


--
-- Name: socialaccount_socialaccount_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('socialaccount_socialaccount_id_seq', 1, false);


--
-- Data for Name: socialaccount_socialapp; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY socialaccount_socialapp (id, provider, name, client_id, secret, key) FROM stdin;
\.


--
-- Name: socialaccount_socialapp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('socialaccount_socialapp_id_seq', 1, false);


--
-- Data for Name: socialaccount_socialapp_sites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY socialaccount_socialapp_sites (id, socialapp_id, site_id) FROM stdin;
\.


--
-- Name: socialaccount_socialapp_sites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('socialaccount_socialapp_sites_id_seq', 1, false);


--
-- Data for Name: socialaccount_socialtoken; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY socialaccount_socialtoken (id, token, token_secret, expires_at, account_id, app_id) FROM stdin;
\.


--
-- Name: socialaccount_socialtoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('socialaccount_socialtoken_id_seq', 1, false);


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: students_idtype; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY students_idtype (id, name) FROM stdin;
1	type
\.


--
-- Name: students_idtype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('students_idtype_id_seq', 1, true);


--
-- Data for Name: students_language; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY students_language (id, name) FROM stdin;
1	frensh
\.


--
-- Name: students_language_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('students_language_id_seq', 1, true);


--
-- Data for Name: students_nationality; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY students_nationality (id, name) FROM stdin;
1	syrien
\.


--
-- Name: students_nationality_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('students_nationality_id_seq', 1, true);


--
-- Data for Name: students_student; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY students_student (id, created, modified, first_name, last_name, father_name, full_name, mother_fullname, sex, birthday_year, birthday_month, birthday_day, phone, id_number, address, nationality_id, id_type_id, mother_firstname, mother_lastname, number, age) FROM stdin;
1	2016-08-22 20:35:25.093465+03	2016-08-22 20:35:25.093875+03	\N	\N	\N	cervrevrvd  ef	dvd dfdfd	Female	1994	3	5	refdfdfdf	cdcdcsdssc	cccsdcsdcs	1	\N	\N	\N	\N	\N
2	2016-08-22 21:09:21.346025+03	2016-08-22 21:09:21.346321+03	\N	\N	\N	fffffffff	fffffffff	Male	1990	2	3	fvs verg eve	defsdfss	dsdacscarferer	1	\N	\N	\N	\N	\N
3	2016-08-23 15:42:31.609797+03	2016-08-23 15:42:31.610178+03	\N	\N	\N	dkjshd jhkshjgdhj	fkjd shfjkhdsjkh	Female	1995	5	4	fjkdhsjkh	545454545	dnb hfghjsgh	1	\N	\N	\N	\N	\N
5	2016-08-23 22:23:01.533788+03	2016-08-23 22:23:01.534128+03	\N	\N	\N	ddddd	ddddd	Male	1993	4	3	rrrrrrr	dddddd	eeeee	1	1	\N	\N	559543050095430500M341993	\N
6	2016-08-25 14:44:58.094181+03	2016-08-25 14:44:58.094714+03	\N	\N	\N	jh gjhbfhcbcc	k jhkjg jhg hjgfjh fghfg	Female	1994	5	6	mnb mnbmnb	m,b mnbmnb	mnbmnbm mn	1	1	\N	\N	13241417147456175969641F651994	\N
7	2016-08-25 14:50:59.649494+03	2016-08-25 14:50:59.649829+03	\N	\N	\N	gfdfgsdfds	jhfgdfgdfgs	Female	1993	4	4	,m mnbmnbnmb	,mn,mnm,n	kj jk bnmvbmnvmn	1	1	\N	\N	10111161258914557656884F441993	\N
8	2016-08-26 16:04:22.391838+03	2016-08-26 16:04:22.392378+03	\N	\N	\N	gfdfgdfgf	gfdfgsdfsf	Female	1994	4	4	,h bmnbmnbnmmn	,mnm,bmn	hj ghjghjg	1	1	\N	\N	91017632104391161258462F441994	\N
\.


--
-- Name: students_student_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('students_student_id_seq', 8, true);


--
-- Data for Name: users_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY users_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, phone_number, partner_id, school_id, location_id) FROM stdin;
2	pbkdf2_sha256$24000$bTWH0VRXcqci$r3YC/JwW/9HhLhAGJ1TpqJa46cUuAjyuS4xfaUZhsxw=	2016-08-28 17:42:02.549789+03	f	ali.chamseddine			ali.chamseddine21@gmail.com	f	t	2016-08-19 11:47:10+03		\N	\N	\N
1	pbkdf2_sha256$24000$I4nE43ObkH5P$oV/R/RfkGUzdMXPPRKCK1/lm7qPagjxh5f/VGPM6Isw=	2016-08-29 19:08:14.383365+03	t	achamseddine			achamseddine@unicef.org	t	t	2016-08-19 11:44:58.229042+03	\N	\N	\N	\N
\.


--
-- Data for Name: users_user_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY users_user_groups (id, user_id, group_id) FROM stdin;
1	2	1
\.


--
-- Name: users_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('users_user_groups_id_seq', 1, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('users_user_id_seq', 2, true);


--
-- Data for Name: users_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY users_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Name: users_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('users_user_user_permissions_id_seq', 1, false);


--
-- Name: account_emailaddress_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_emailaddress
    ADD CONSTRAINT account_emailaddress_email_key UNIQUE (email);


--
-- Name: account_emailaddress_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_emailaddress
    ADD CONSTRAINT account_emailaddress_pkey PRIMARY KEY (id);


--
-- Name: account_emailconfirmation_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_emailconfirmation
    ADD CONSTRAINT account_emailconfirmation_key_key UNIQUE (key);


--
-- Name: account_emailconfirmation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_emailconfirmation
    ADD CONSTRAINT account_emailconfirmation_pkey PRIMARY KEY (id);


--
-- Name: alp_extracolumn_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_extracolumn
    ADD CONSTRAINT alp_extracolumn_pkey PRIMARY KEY (id);


--
-- Name: alp_outreach_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_outreach
    ADD CONSTRAINT alp_outreach_pkey PRIMARY KEY (id);


--
-- Name: attendances_attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY attendances_attendance
    ADD CONSTRAINT attendances_attendance_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions_group_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_content_type_id_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: authtoken_token_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY authtoken_token
    ADD CONSTRAINT authtoken_token_pkey PRIMARY KEY (key);


--
-- Name: authtoken_token_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_key UNIQUE (user_id);


--
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_app_label_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: django_site_domain_a2e37b91_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_domain_a2e37b91_uniq UNIQUE (domain);


--
-- Name: django_site_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);


--
-- Name: eav_attribute_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_attribute
    ADD CONSTRAINT eav_attribute_pkey PRIMARY KEY (id);


--
-- Name: eav_attribute_site_id_e0eb0ff0_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_attribute
    ADD CONSTRAINT eav_attribute_site_id_e0eb0ff0_uniq UNIQUE (site_id, slug);


--
-- Name: eav_enumgroup_enums_enumgroup_id_8d3d15af_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_enumgroup_enums
    ADD CONSTRAINT eav_enumgroup_enums_enumgroup_id_8d3d15af_uniq UNIQUE (enumgroup_id, enumvalue_id);


--
-- Name: eav_enumgroup_enums_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_enumgroup_enums
    ADD CONSTRAINT eav_enumgroup_enums_pkey PRIMARY KEY (id);


--
-- Name: eav_enumgroup_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_enumgroup
    ADD CONSTRAINT eav_enumgroup_name_key UNIQUE (name);


--
-- Name: eav_enumgroup_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_enumgroup
    ADD CONSTRAINT eav_enumgroup_pkey PRIMARY KEY (id);


--
-- Name: eav_enumvalue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_enumvalue
    ADD CONSTRAINT eav_enumvalue_pkey PRIMARY KEY (id);


--
-- Name: eav_enumvalue_value_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_enumvalue
    ADD CONSTRAINT eav_enumvalue_value_key UNIQUE (value);


--
-- Name: eav_value_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_value
    ADD CONSTRAINT eav_value_pkey PRIMARY KEY (id);


--
-- Name: locations_location_name_fc4d5026_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY locations_location
    ADD CONSTRAINT locations_location_name_fc4d5026_uniq UNIQUE (name, gateway_id, p_code);


--
-- Name: locations_location_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY locations_location
    ADD CONSTRAINT locations_location_pkey PRIMARY KEY (id);


--
-- Name: locations_locationtype_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY locations_locationtype
    ADD CONSTRAINT locations_locationtype_name_key UNIQUE (name);


--
-- Name: locations_locationtype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY locations_locationtype
    ADD CONSTRAINT locations_locationtype_pkey PRIMARY KEY (id);


--
-- Name: registrations_phone_extension_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_phone
    ADD CONSTRAINT registrations_phone_extension_key UNIQUE (extension);


--
-- Name: registrations_phone_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_phone
    ADD CONSTRAINT registrations_phone_number_key UNIQUE (number);


--
-- Name: registrations_phone_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_phone
    ADD CONSTRAINT registrations_phone_pkey PRIMARY KEY (id);


--
-- Name: registrations_phone_prefix_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_phone
    ADD CONSTRAINT registrations_phone_prefix_key UNIQUE (prefix);


--
-- Name: registrations_registeringadult_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registeringadult
    ADD CONSTRAINT registrations_registeringadult_number_key UNIQUE (number);


--
-- Name: registrations_registeringadult_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registeringadult
    ADD CONSTRAINT registrations_registeringadult_pkey PRIMARY KEY (id);


--
-- Name: registrations_registration_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registration
    ADD CONSTRAINT registrations_registration_pkey PRIMARY KEY (id);


--
-- Name: schools_classlevel_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_classlevel
    ADD CONSTRAINT schools_classlevel_name_key UNIQUE (name);


--
-- Name: schools_classlevel_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_classlevel
    ADD CONSTRAINT schools_classlevel_pkey PRIMARY KEY (id);


--
-- Name: schools_classroom_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_classroom
    ADD CONSTRAINT schools_classroom_name_key UNIQUE (name);


--
-- Name: schools_classroom_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_classroom
    ADD CONSTRAINT schools_classroom_pkey PRIMARY KEY (id);


--
-- Name: schools_course_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_course
    ADD CONSTRAINT schools_course_name_key UNIQUE (name);


--
-- Name: schools_course_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_course
    ADD CONSTRAINT schools_course_pkey PRIMARY KEY (id);


--
-- Name: schools_educationlevel_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_educationlevel
    ADD CONSTRAINT schools_educationlevel_name_key UNIQUE (name);


--
-- Name: schools_educationlevel_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_educationlevel
    ADD CONSTRAINT schools_educationlevel_pkey PRIMARY KEY (id);


--
-- Name: schools_grade_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_grade
    ADD CONSTRAINT schools_grade_name_key UNIQUE (name);


--
-- Name: schools_grade_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_grade
    ADD CONSTRAINT schools_grade_pkey PRIMARY KEY (id);


--
-- Name: schools_partnerorganization_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_partnerorganization
    ADD CONSTRAINT schools_partnerorganization_name_key UNIQUE (name);


--
-- Name: schools_partnerorganization_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_partnerorganization
    ADD CONSTRAINT schools_partnerorganization_pkey PRIMARY KEY (id);


--
-- Name: schools_school_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_school
    ADD CONSTRAINT schools_school_number_key UNIQUE (number);


--
-- Name: schools_school_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_school
    ADD CONSTRAINT schools_school_pkey PRIMARY KEY (id);


--
-- Name: schools_section_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_section
    ADD CONSTRAINT schools_section_name_key UNIQUE (name);


--
-- Name: schools_section_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_section
    ADD CONSTRAINT schools_section_pkey PRIMARY KEY (id);


--
-- Name: socialaccount_socialaccount_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialaccount
    ADD CONSTRAINT socialaccount_socialaccount_pkey PRIMARY KEY (id);


--
-- Name: socialaccount_socialaccount_provider_fc810c6e_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialaccount
    ADD CONSTRAINT socialaccount_socialaccount_provider_fc810c6e_uniq UNIQUE (provider, uid);


--
-- Name: socialaccount_socialapp_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialapp
    ADD CONSTRAINT socialaccount_socialapp_pkey PRIMARY KEY (id);


--
-- Name: socialaccount_socialapp_sites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialapp_sites
    ADD CONSTRAINT socialaccount_socialapp_sites_pkey PRIMARY KEY (id);


--
-- Name: socialaccount_socialapp_sites_socialapp_id_71a9a768_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialapp_sites
    ADD CONSTRAINT socialaccount_socialapp_sites_socialapp_id_71a9a768_uniq UNIQUE (socialapp_id, site_id);


--
-- Name: socialaccount_socialtoken_app_id_fca4e0ac_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialtoken
    ADD CONSTRAINT socialaccount_socialtoken_app_id_fca4e0ac_uniq UNIQUE (app_id, account_id);


--
-- Name: socialaccount_socialtoken_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialtoken
    ADD CONSTRAINT socialaccount_socialtoken_pkey PRIMARY KEY (id);


--
-- Name: students_idtype_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_idtype
    ADD CONSTRAINT students_idtype_name_key UNIQUE (name);


--
-- Name: students_idtype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_idtype
    ADD CONSTRAINT students_idtype_pkey PRIMARY KEY (id);


--
-- Name: students_language_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_language
    ADD CONSTRAINT students_language_name_key UNIQUE (name);


--
-- Name: students_language_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_language
    ADD CONSTRAINT students_language_pkey PRIMARY KEY (id);


--
-- Name: students_nationality_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_nationality
    ADD CONSTRAINT students_nationality_name_key UNIQUE (name);


--
-- Name: students_nationality_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_nationality
    ADD CONSTRAINT students_nationality_pkey PRIMARY KEY (id);


--
-- Name: students_student_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_student
    ADD CONSTRAINT students_student_number_key UNIQUE (number);


--
-- Name: students_student_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_student
    ADD CONSTRAINT students_student_pkey PRIMARY KEY (id);


--
-- Name: users_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user_groups
    ADD CONSTRAINT users_user_groups_pkey PRIMARY KEY (id);


--
-- Name: users_user_groups_user_id_b88eab82_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user_groups
    ADD CONSTRAINT users_user_groups_user_id_b88eab82_uniq UNIQUE (user_id, group_id);


--
-- Name: users_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user
    ADD CONSTRAINT users_user_pkey PRIMARY KEY (id);


--
-- Name: users_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user_user_permissions
    ADD CONSTRAINT users_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: users_user_user_permissions_user_id_43338c45_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user_user_permissions
    ADD CONSTRAINT users_user_user_permissions_user_id_43338c45_uniq UNIQUE (user_id, permission_id);


--
-- Name: users_user_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user
    ADD CONSTRAINT users_user_username_key UNIQUE (username);


--
-- Name: account_emailaddress_e8701ad4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX account_emailaddress_e8701ad4 ON account_emailaddress USING btree (user_id);


--
-- Name: account_emailaddress_email_03be32b2_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX account_emailaddress_email_03be32b2_like ON account_emailaddress USING btree (email varchar_pattern_ops);


--
-- Name: account_emailconfirmation_6f1edeac; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX account_emailconfirmation_6f1edeac ON account_emailconfirmation USING btree (email_address_id);


--
-- Name: account_emailconfirmation_key_f43612bd_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX account_emailconfirmation_key_f43612bd_like ON account_emailconfirmation USING btree (key varchar_pattern_ops);


--
-- Name: alp_extracolumn_5e7b1936; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX alp_extracolumn_5e7b1936 ON alp_extracolumn USING btree (owner_id);


--
-- Name: alp_outreach_15e2294c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX alp_outreach_15e2294c ON alp_outreach USING btree (preferred_language_id);


--
-- Name: alp_outreach_30a811f6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX alp_outreach_30a811f6 ON alp_outreach USING btree (student_id);


--
-- Name: alp_outreach_4e98b6eb; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX alp_outreach_4e98b6eb ON alp_outreach USING btree (partner_id);


--
-- Name: alp_outreach_5e7b1936; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX alp_outreach_5e7b1936 ON alp_outreach USING btree (owner_id);


--
-- Name: alp_outreach_5fc7164b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX alp_outreach_5fc7164b ON alp_outreach USING btree (school_id);


--
-- Name: alp_outreach_7d0bdb3b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX alp_outreach_7d0bdb3b ON alp_outreach USING btree (last_education_level_id);


--
-- Name: alp_outreach_b02106cc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX alp_outreach_b02106cc ON alp_outreach USING btree (last_class_level_id);


--
-- Name: alp_outreach_e274a5da; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX alp_outreach_e274a5da ON alp_outreach USING btree (location_id);


--
-- Name: attendances_attendance_30a811f6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX attendances_attendance_30a811f6 ON attendances_attendance USING btree (student_id);


--
-- Name: attendances_attendance_5e7b1936; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX attendances_attendance_5e7b1936 ON attendances_attendance USING btree (owner_id);


--
-- Name: attendances_attendance_5fc7164b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX attendances_attendance_5fc7164b ON attendances_attendance USING btree (school_id);


--
-- Name: attendances_attendance_837734a3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX attendances_attendance_837734a3 ON attendances_attendance USING btree (classroom_id);


--
-- Name: attendances_attendance_af641552; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX attendances_attendance_af641552 ON attendances_attendance USING btree (validation_owner_id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_name_a6ea08ec_like ON auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_0e939a4f; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_0e939a4f ON auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_8373b171; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_8373b171 ON auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_417f1b1c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_permission_417f1b1c ON auth_permission USING btree (content_type_id);


--
-- Name: authtoken_token_key_10f0b77e_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX authtoken_token_key_10f0b77e_like ON authtoken_token USING btree (key varchar_pattern_ops);


--
-- Name: django_admin_log_417f1b1c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_417f1b1c ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_e8701ad4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_e8701ad4 ON django_admin_log USING btree (user_id);


--
-- Name: django_session_de54fa62; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_de54fa62 ON django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_session_key_c0390e0f_like ON django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: django_site_domain_a2e37b91_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_site_domain_a2e37b91_like ON django_site USING btree (domain varchar_pattern_ops);


--
-- Name: eav_attribute_2dbcba41; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_attribute_2dbcba41 ON eav_attribute USING btree (slug);


--
-- Name: eav_attribute_5e7b1936; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_attribute_5e7b1936 ON eav_attribute USING btree (owner_id);


--
-- Name: eav_attribute_9365d6e7; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_attribute_9365d6e7 ON eav_attribute USING btree (site_id);


--
-- Name: eav_attribute_db68ddb3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_attribute_db68ddb3 ON eav_attribute USING btree (enum_group_id);


--
-- Name: eav_attribute_slug_1c525d06_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_attribute_slug_1c525d06_like ON eav_attribute USING btree (slug varchar_pattern_ops);


--
-- Name: eav_enumgroup_enums_6298cf2b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_enumgroup_enums_6298cf2b ON eav_enumgroup_enums USING btree (enumvalue_id);


--
-- Name: eav_enumgroup_enums_d7282c11; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_enumgroup_enums_d7282c11 ON eav_enumgroup_enums USING btree (enumgroup_id);


--
-- Name: eav_enumgroup_name_1077d89b_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_enumgroup_name_1077d89b_like ON eav_enumgroup USING btree (name varchar_pattern_ops);


--
-- Name: eav_enumvalue_value_027e7652_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_enumvalue_value_027e7652_like ON eav_enumvalue USING btree (value varchar_pattern_ops);


--
-- Name: eav_value_1303651b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_value_1303651b ON eav_value USING btree (generic_value_ct_id);


--
-- Name: eav_value_1f704274; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_value_1f704274 ON eav_value USING btree (value_enum_id);


--
-- Name: eav_value_c0ce35ac; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_value_c0ce35ac ON eav_value USING btree (entity_ct_id);


--
-- Name: eav_value_e582ed73; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX eav_value_e582ed73 ON eav_value USING btree (attribute_id);


--
-- Name: locations_location_1e9cd8d4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX locations_location_1e9cd8d4 ON locations_location USING btree (gateway_id);


--
-- Name: locations_location_3cfbd988; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX locations_location_3cfbd988 ON locations_location USING btree (rght);


--
-- Name: locations_location_656442a0; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX locations_location_656442a0 ON locations_location USING btree (tree_id);


--
-- Name: locations_location_6be37982; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX locations_location_6be37982 ON locations_location USING btree (parent_id);


--
-- Name: locations_location_c9e9a848; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX locations_location_c9e9a848 ON locations_location USING btree (level);


--
-- Name: locations_location_caf7cc51; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX locations_location_caf7cc51 ON locations_location USING btree (lft);


--
-- Name: locations_locationtype_name_f6c71ea6_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX locations_locationtype_name_f6c71ea6_like ON locations_locationtype USING btree (name varchar_pattern_ops);


--
-- Name: registrations_phone_2213621d; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_phone_2213621d ON registrations_phone USING btree (adult_id);


--
-- Name: registrations_phone_extension_7416df41_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_phone_extension_7416df41_like ON registrations_phone USING btree (extension varchar_pattern_ops);


--
-- Name: registrations_phone_number_70d5312e_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_phone_number_70d5312e_like ON registrations_phone USING btree (number varchar_pattern_ops);


--
-- Name: registrations_phone_prefix_808de564_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_phone_prefix_808de564_like ON registrations_phone USING btree (prefix varchar_pattern_ops);


--
-- Name: registrations_registeringadult_4503f927; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_registeringadult_4503f927 ON registrations_registeringadult USING btree (id_type_id);


--
-- Name: registrations_registeringadult_5fc7164b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_registeringadult_5fc7164b ON registrations_registeringadult USING btree (school_id);


--
-- Name: registrations_registeringadult_663581ef; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_registeringadult_663581ef ON registrations_registeringadult USING btree (nationality_id);


--
-- Name: registrations_registeringadult_number_1af7162d_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_registeringadult_number_1af7162d_like ON registrations_registeringadult USING btree (number varchar_pattern_ops);


--
-- Name: registrations_registration_30a811f6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_registration_30a811f6 ON registrations_registration USING btree (student_id);


--
-- Name: registrations_registration_5c853be8; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_registration_5c853be8 ON registrations_registration USING btree (grade_id);


--
-- Name: registrations_registration_5e7b1936; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_registration_5e7b1936 ON registrations_registration USING btree (owner_id);


--
-- Name: registrations_registration_5fc7164b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_registration_5fc7164b ON registrations_registration USING btree (school_id);


--
-- Name: registrations_registration_730f6511; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_registration_730f6511 ON registrations_registration USING btree (section_id);


--
-- Name: registrations_registration_768d6829; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_registration_768d6829 ON registrations_registration USING btree (registering_adult_id);


--
-- Name: registrations_registration_837734a3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX registrations_registration_837734a3 ON registrations_registration USING btree (classroom_id);


--
-- Name: schools_classlevel_name_26bfe828_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schools_classlevel_name_26bfe828_like ON schools_classlevel USING btree (name varchar_pattern_ops);


--
-- Name: schools_classroom_5c853be8; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schools_classroom_5c853be8 ON schools_classroom USING btree (grade_id);


--
-- Name: schools_classroom_5fc7164b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schools_classroom_5fc7164b ON schools_classroom USING btree (school_id);


--
-- Name: schools_classroom_730f6511; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schools_classroom_730f6511 ON schools_classroom USING btree (section_id);


--
-- Name: schools_classroom_name_efc38097_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schools_classroom_name_efc38097_like ON schools_classroom USING btree (name varchar_pattern_ops);


--
-- Name: schools_course_name_03ad74dd_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schools_course_name_03ad74dd_like ON schools_course USING btree (name varchar_pattern_ops);


--
-- Name: schools_educationlevel_name_86b9f1fa_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schools_educationlevel_name_86b9f1fa_like ON schools_educationlevel USING btree (name varchar_pattern_ops);


--
-- Name: schools_grade_name_574b5c1f_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schools_grade_name_574b5c1f_like ON schools_grade USING btree (name varchar_pattern_ops);


--
-- Name: schools_partnerorganization_name_dba375db_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schools_partnerorganization_name_dba375db_like ON schools_partnerorganization USING btree (name varchar_pattern_ops);


--
-- Name: schools_school_e274a5da; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schools_school_e274a5da ON schools_school USING btree (location_id);


--
-- Name: schools_school_number_a169e267_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schools_school_number_a169e267_like ON schools_school USING btree (number varchar_pattern_ops);


--
-- Name: schools_section_name_5108f35d_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schools_section_name_5108f35d_like ON schools_section USING btree (name varchar_pattern_ops);


--
-- Name: socialaccount_socialaccount_e8701ad4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX socialaccount_socialaccount_e8701ad4 ON socialaccount_socialaccount USING btree (user_id);


--
-- Name: socialaccount_socialapp_sites_9365d6e7; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX socialaccount_socialapp_sites_9365d6e7 ON socialaccount_socialapp_sites USING btree (site_id);


--
-- Name: socialaccount_socialapp_sites_fe95b0a0; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX socialaccount_socialapp_sites_fe95b0a0 ON socialaccount_socialapp_sites USING btree (socialapp_id);


--
-- Name: socialaccount_socialtoken_8a089c2a; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX socialaccount_socialtoken_8a089c2a ON socialaccount_socialtoken USING btree (account_id);


--
-- Name: socialaccount_socialtoken_f382adfe; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX socialaccount_socialtoken_f382adfe ON socialaccount_socialtoken USING btree (app_id);


--
-- Name: students_idtype_name_f3ed1ca0_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_idtype_name_f3ed1ca0_like ON students_idtype USING btree (name varchar_pattern_ops);


--
-- Name: students_language_name_26172f40_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_language_name_26172f40_like ON students_language USING btree (name varchar_pattern_ops);


--
-- Name: students_nationality_name_b83296bd_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_nationality_name_b83296bd_like ON students_nationality USING btree (name varchar_pattern_ops);


--
-- Name: students_student_4503f927; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_student_4503f927 ON students_student USING btree (id_type_id);


--
-- Name: students_student_663581ef; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_student_663581ef ON students_student USING btree (nationality_id);


--
-- Name: users_user_4e98b6eb; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_user_4e98b6eb ON users_user USING btree (partner_id);


--
-- Name: users_user_5fc7164b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_user_5fc7164b ON users_user USING btree (school_id);


--
-- Name: users_user_e274a5da; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_user_e274a5da ON users_user USING btree (location_id);


--
-- Name: users_user_groups_0e939a4f; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_user_groups_0e939a4f ON users_user_groups USING btree (group_id);


--
-- Name: users_user_groups_e8701ad4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_user_groups_e8701ad4 ON users_user_groups USING btree (user_id);


--
-- Name: users_user_user_permissions_8373b171; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_user_user_permissions_8373b171 ON users_user_user_permissions USING btree (permission_id);


--
-- Name: users_user_user_permissions_e8701ad4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_user_user_permissions_e8701ad4 ON users_user_user_permissions USING btree (user_id);


--
-- Name: users_user_username_06e46fe6_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_user_username_06e46fe6_like ON users_user USING btree (username varchar_pattern_ops);


--
-- Name: D19127553b27243c1097bfc5b8732159; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registration
    ADD CONSTRAINT "D19127553b27243c1097bfc5b8732159" FOREIGN KEY (registering_adult_id) REFERENCES registrations_registeringadult(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: a_last_education_level_id_dbe25bea_fk_schools_educationlevel_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_outreach
    ADD CONSTRAINT a_last_education_level_id_dbe25bea_fk_schools_educationlevel_id FOREIGN KEY (last_education_level_id) REFERENCES schools_educationlevel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: account_em_email_address_id_5b7f8c58_fk_account_emailaddress_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_emailconfirmation
    ADD CONSTRAINT account_em_email_address_id_5b7f8c58_fk_account_emailaddress_id FOREIGN KEY (email_address_id) REFERENCES account_emailaddress(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: account_emailaddress_user_id_2c513194_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_emailaddress
    ADD CONSTRAINT account_emailaddress_user_id_2c513194_fk_users_user_id FOREIGN KEY (user_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: alp_extracolumn_owner_id_c7d1d68d_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_extracolumn
    ADD CONSTRAINT alp_extracolumn_owner_id_c7d1d68d_fk_users_user_id FOREIGN KEY (owner_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: alp_outr_preferred_language_id_6c7e6cd8_fk_students_language_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_outreach
    ADD CONSTRAINT alp_outr_preferred_language_id_6c7e6cd8_fk_students_language_id FOREIGN KEY (preferred_language_id) REFERENCES students_language(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: alp_outre_last_class_level_id_76db489b_fk_schools_classlevel_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_outreach
    ADD CONSTRAINT alp_outre_last_class_level_id_76db489b_fk_schools_classlevel_id FOREIGN KEY (last_class_level_id) REFERENCES schools_classlevel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: alp_outre_partner_id_cd42a843_fk_schools_partnerorganization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_outreach
    ADD CONSTRAINT alp_outre_partner_id_cd42a843_fk_schools_partnerorganization_id FOREIGN KEY (partner_id) REFERENCES schools_partnerorganization(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: alp_outreach_location_id_e48185ed_fk_locations_location_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_outreach
    ADD CONSTRAINT alp_outreach_location_id_e48185ed_fk_locations_location_id FOREIGN KEY (location_id) REFERENCES locations_location(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: alp_outreach_owner_id_38030f26_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_outreach
    ADD CONSTRAINT alp_outreach_owner_id_38030f26_fk_users_user_id FOREIGN KEY (owner_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: alp_outreach_school_id_077b1d5c_fk_schools_school_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_outreach
    ADD CONSTRAINT alp_outreach_school_id_077b1d5c_fk_schools_school_id FOREIGN KEY (school_id) REFERENCES schools_school(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: alp_outreach_student_id_3895dcef_fk_students_student_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alp_outreach
    ADD CONSTRAINT alp_outreach_student_id_3895dcef_fk_students_student_id FOREIGN KEY (student_id) REFERENCES students_student(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: attendances_atten_classroom_id_91922307_fk_schools_classroom_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY attendances_attendance
    ADD CONSTRAINT attendances_atten_classroom_id_91922307_fk_schools_classroom_id FOREIGN KEY (classroom_id) REFERENCES schools_classroom(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: attendances_atten_validation_owner_id_8207bbf2_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY attendances_attendance
    ADD CONSTRAINT attendances_atten_validation_owner_id_8207bbf2_fk_users_user_id FOREIGN KEY (validation_owner_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: attendances_attendan_student_id_1eada1c0_fk_students_student_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY attendances_attendance
    ADD CONSTRAINT attendances_attendan_student_id_1eada1c0_fk_students_student_id FOREIGN KEY (student_id) REFERENCES students_student(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: attendances_attendance_owner_id_1ba269a5_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY attendances_attendance
    ADD CONSTRAINT attendances_attendance_owner_id_1ba269a5_fk_users_user_id FOREIGN KEY (owner_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: attendances_attendance_school_id_fe0f3bd5_fk_schools_school_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY attendances_attendance
    ADD CONSTRAINT attendances_attendance_school_id_fe0f3bd5_fk_schools_school_id FOREIGN KEY (school_id) REFERENCES schools_school(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permiss_permission_id_84c5c92e_fk_auth_permission_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permiss_permission_id_84c5c92e_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permiss_content_type_id_2f476e4b_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permiss_content_type_id_2f476e4b_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: authtoken_token_user_id_35299eff_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_35299eff_fk_users_user_id FOREIGN KEY (user_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_content_type_id_c4bce8eb_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_content_type_id_c4bce8eb_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_user_id_c564eba6_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_users_user_id FOREIGN KEY (user_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: eav_attribute_enum_group_id_47628614_fk_eav_enumgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_attribute
    ADD CONSTRAINT eav_attribute_enum_group_id_47628614_fk_eav_enumgroup_id FOREIGN KEY (enum_group_id) REFERENCES eav_enumgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: eav_attribute_owner_id_a28893c7_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_attribute
    ADD CONSTRAINT eav_attribute_owner_id_a28893c7_fk_users_user_id FOREIGN KEY (owner_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: eav_attribute_site_id_aef37747_fk_django_site_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_attribute
    ADD CONSTRAINT eav_attribute_site_id_aef37747_fk_django_site_id FOREIGN KEY (site_id) REFERENCES django_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: eav_enumgroup_enums_enumgroup_id_cb57b62e_fk_eav_enumgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_enumgroup_enums
    ADD CONSTRAINT eav_enumgroup_enums_enumgroup_id_cb57b62e_fk_eav_enumgroup_id FOREIGN KEY (enumgroup_id) REFERENCES eav_enumgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: eav_enumgroup_enums_enumvalue_id_bc5715f9_fk_eav_enumvalue_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_enumgroup_enums
    ADD CONSTRAINT eav_enumgroup_enums_enumvalue_id_bc5715f9_fk_eav_enumvalue_id FOREIGN KEY (enumvalue_id) REFERENCES eav_enumvalue(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: eav_valu_generic_value_ct_id_d4681436_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_value
    ADD CONSTRAINT eav_valu_generic_value_ct_id_d4681436_fk_django_content_type_id FOREIGN KEY (generic_value_ct_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: eav_value_attribute_id_6fd472ba_fk_eav_attribute_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_value
    ADD CONSTRAINT eav_value_attribute_id_6fd472ba_fk_eav_attribute_id FOREIGN KEY (attribute_id) REFERENCES eav_attribute(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: eav_value_entity_ct_id_5cfd530e_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_value
    ADD CONSTRAINT eav_value_entity_ct_id_5cfd530e_fk_django_content_type_id FOREIGN KEY (entity_ct_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: eav_value_value_enum_id_86e48f74_fk_eav_enumvalue_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY eav_value
    ADD CONSTRAINT eav_value_value_enum_id_86e48f74_fk_eav_enumvalue_id FOREIGN KEY (value_enum_id) REFERENCES eav_enumvalue(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: locations_loca_gateway_id_248fb7f2_fk_locations_locationtype_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY locations_location
    ADD CONSTRAINT locations_loca_gateway_id_248fb7f2_fk_locations_locationtype_id FOREIGN KEY (gateway_id) REFERENCES locations_locationtype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: locations_location_parent_id_d8d97084_fk_locations_location_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY locations_location
    ADD CONSTRAINT locations_location_parent_id_d8d97084_fk_locations_location_id FOREIGN KEY (parent_id) REFERENCES locations_location(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: registra_adult_id_e46950ad_fk_registrations_registeringadult_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_phone
    ADD CONSTRAINT registra_adult_id_e46950ad_fk_registrations_registeringadult_id FOREIGN KEY (adult_id) REFERENCES registrations_registeringadult(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: registration_nationality_id_578b1e15_fk_students_nationality_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registeringadult
    ADD CONSTRAINT registration_nationality_id_578b1e15_fk_students_nationality_id FOREIGN KEY (nationality_id) REFERENCES students_nationality(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: registrations_reg_classroom_id_d9e473bb_fk_schools_classroom_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registration
    ADD CONSTRAINT registrations_reg_classroom_id_d9e473bb_fk_schools_classroom_id FOREIGN KEY (classroom_id) REFERENCES schools_classroom(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: registrations_regist_student_id_4904cb27_fk_students_student_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registration
    ADD CONSTRAINT registrations_regist_student_id_4904cb27_fk_students_student_id FOREIGN KEY (student_id) REFERENCES students_student(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: registrations_registe_id_type_id_e4c93f11_fk_students_idtype_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registeringadult
    ADD CONSTRAINT registrations_registe_id_type_id_e4c93f11_fk_students_idtype_id FOREIGN KEY (id_type_id) REFERENCES students_idtype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: registrations_registeri_school_id_d807c123_fk_schools_school_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registeringadult
    ADD CONSTRAINT registrations_registeri_school_id_d807c123_fk_schools_school_id FOREIGN KEY (school_id) REFERENCES schools_school(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: registrations_registr_section_id_caadbfce_fk_schools_section_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registration
    ADD CONSTRAINT registrations_registr_section_id_caadbfce_fk_schools_section_id FOREIGN KEY (section_id) REFERENCES schools_section(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: registrations_registrat_school_id_4f7d3b02_fk_schools_school_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registration
    ADD CONSTRAINT registrations_registrat_school_id_4f7d3b02_fk_schools_school_id FOREIGN KEY (school_id) REFERENCES schools_school(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: registrations_registratio_grade_id_cee9e24f_fk_schools_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registration
    ADD CONSTRAINT registrations_registratio_grade_id_cee9e24f_fk_schools_grade_id FOREIGN KEY (grade_id) REFERENCES schools_grade(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: registrations_registration_owner_id_31fe4584_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY registrations_registration
    ADD CONSTRAINT registrations_registration_owner_id_31fe4584_fk_users_user_id FOREIGN KEY (owner_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: schools_classroom_grade_id_f5227cf4_fk_schools_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_classroom
    ADD CONSTRAINT schools_classroom_grade_id_f5227cf4_fk_schools_grade_id FOREIGN KEY (grade_id) REFERENCES schools_grade(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: schools_classroom_school_id_b093c6a4_fk_schools_school_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_classroom
    ADD CONSTRAINT schools_classroom_school_id_b093c6a4_fk_schools_school_id FOREIGN KEY (school_id) REFERENCES schools_school(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: schools_classroom_section_id_60c2e1c8_fk_schools_section_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_classroom
    ADD CONSTRAINT schools_classroom_section_id_60c2e1c8_fk_schools_section_id FOREIGN KEY (section_id) REFERENCES schools_section(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: schools_school_location_id_25f4e156_fk_locations_location_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schools_school
    ADD CONSTRAINT schools_school_location_id_25f4e156_fk_locations_location_id FOREIGN KEY (location_id) REFERENCES locations_location(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: socialacc_account_id_951f210e_fk_socialaccount_socialaccount_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialtoken
    ADD CONSTRAINT socialacc_account_id_951f210e_fk_socialaccount_socialaccount_id FOREIGN KEY (account_id) REFERENCES socialaccount_socialaccount(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: socialaccou_socialapp_id_97fb6e7d_fk_socialaccount_socialapp_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialapp_sites
    ADD CONSTRAINT socialaccou_socialapp_id_97fb6e7d_fk_socialaccount_socialapp_id FOREIGN KEY (socialapp_id) REFERENCES socialaccount_socialapp(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: socialaccount_soc_app_id_636a42d7_fk_socialaccount_socialapp_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialtoken
    ADD CONSTRAINT socialaccount_soc_app_id_636a42d7_fk_socialaccount_socialapp_id FOREIGN KEY (app_id) REFERENCES socialaccount_socialapp(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: socialaccount_socialaccount_user_id_8146e70c_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialaccount
    ADD CONSTRAINT socialaccount_socialaccount_user_id_8146e70c_fk_users_user_id FOREIGN KEY (user_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: socialaccount_socialapp_site_site_id_2579dee5_fk_django_site_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY socialaccount_socialapp_sites
    ADD CONSTRAINT socialaccount_socialapp_site_site_id_2579dee5_fk_django_site_id FOREIGN KEY (site_id) REFERENCES django_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: students_stu_nationality_id_e96db571_fk_students_nationality_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_student
    ADD CONSTRAINT students_stu_nationality_id_e96db571_fk_students_nationality_id FOREIGN KEY (nationality_id) REFERENCES students_nationality(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: students_student_id_type_id_b6895206_fk_students_idtype_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY students_student
    ADD CONSTRAINT students_student_id_type_id_b6895206_fk_students_idtype_id FOREIGN KEY (id_type_id) REFERENCES students_idtype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_use_partner_id_5c6058d0_fk_schools_partnerorganization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user
    ADD CONSTRAINT users_use_partner_id_5c6058d0_fk_schools_partnerorganization_id FOREIGN KEY (partner_id) REFERENCES schools_partnerorganization(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_groups_group_id_9afc8d0e_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user_groups
    ADD CONSTRAINT users_user_groups_group_id_9afc8d0e_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_groups_user_id_5f6f5a90_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user_groups
    ADD CONSTRAINT users_user_groups_user_id_5f6f5a90_fk_users_user_id FOREIGN KEY (user_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_location_id_9aec1412_fk_locations_location_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user
    ADD CONSTRAINT users_user_location_id_9aec1412_fk_locations_location_id FOREIGN KEY (location_id) REFERENCES locations_location(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_school_id_e82aaa0a_fk_schools_school_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user
    ADD CONSTRAINT users_user_school_id_e82aaa0a_fk_schools_school_id FOREIGN KEY (school_id) REFERENCES schools_school(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_user_pe_permission_id_0b93982e_fk_auth_permission_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user_user_permissions
    ADD CONSTRAINT users_user_user_pe_permission_id_0b93982e_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_user_permissions_user_id_20aca447_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_user_user_permissions
    ADD CONSTRAINT users_user_user_permissions_user_id_20aca447_fk_users_user_id FOREIGN KEY (user_id) REFERENCES users_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: public; Type: ACL; Schema: -; Owner: Ali
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM "Ali";
GRANT ALL ON SCHEMA public TO "Ali";
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

