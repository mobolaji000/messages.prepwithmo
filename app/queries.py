student_table_trigger_text = """
CREATE OR REPLACE FUNCTION student_table_trigger() RETURNS trigger AS $$
   DECLARE
    row RECORD;
    output TEXT;

    BEGIN
    -- Checking the Operation Type
    IF (TG_OP = 'DELETE') THEN
      row = OLD;
    ELSE
      row = NEW;
    END IF;

    output = 'Basics Start-' || 'OPERATION = ' || TG_OP || ' and ID = ' || row.student_id || '-Basics End';

    IF (OLD.student_first_name IS DISTINCT FROM NEW.student_first_name or
        OLD.student_last_name IS DISTINCT FROM NEW.student_last_name or
        OLD.student_phone_number IS DISTINCT FROM NEW.student_phone_number or
        OLD.student_email IS DISTINCT FROM NEW.student_email) THEN
        output = output || 'Student Details Start-' || row.student_first_name || '-' ||
    row.student_last_name || '-' || row.student_phone_number || '-' || row.student_email|| '-Student Details End';
    end if;

    IF (OLD.parent_1_salutation IS DISTINCT FROM NEW.parent_1_salutation or
        OLD.parent_1_first_name IS DISTINCT FROM NEW.parent_1_first_name or
        OLD.parent_1_last_name IS DISTINCT FROM NEW.parent_1_last_name or
        OLD.parent_1_phone_number IS DISTINCT FROM NEW.parent_1_phone_number or
        OLD.parent_1_email IS DISTINCT FROM NEW.parent_1_email) THEN
        output = output || 'Parent_1 Details Start-' || row.parent_1_salutation|| '-' || row.parent_1_first_name ||
                 '-' || row.parent_1_last_name || '-' || row.parent_1_phone_number || '-' || row.parent_1_email || '-Parent_1 Details End' ;
    end if;

    IF (OLD.parent_2_salutation IS DISTINCT FROM NEW.parent_2_salutation or
        OLD.parent_2_first_name IS DISTINCT FROM NEW.parent_2_first_name or
        OLD.parent_2_last_name IS DISTINCT FROM NEW.parent_2_last_name or
        OLD.parent_2_phone_number IS DISTINCT FROM NEW.parent_2_phone_number or
        OLD.parent_2_email IS DISTINCT FROM NEW.parent_2_email) THEN
        output = output || 'Parent_2 Details Start-' || row.parent_2_salutation|| '-' || row.parent_2_first_name ||
                 '-' || row.parent_2_last_name || '-' || row.parent_2_phone_number || '-' || row.parent_2_email || '-Parent_2 Details End';
    end if;

    PERFORM pg_notify('student_table_changed',output);

    -- Returning null because it is an after trigger.
    RETURN NULL;
    END;
   $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS student_table_trigger ON student; CREATE TRIGGER student_table_trigger AFTER update on student for each row execute procedure student_table_trigger();
--DROP TRIGGER IF EXISTS student_table_trigger ON student; CREATE TRIGGER student_table_trigger AFTER insert or update or delete on student for each row execute procedure student_table_trigger();

"""


tutor_table_trigger_text = """
CREATE OR REPLACE FUNCTION tutor_table_trigger() RETURNS trigger AS $$
   DECLARE
    row RECORD;
    output TEXT;

    BEGIN
    -- Checking the Operation Type
    IF (TG_OP = 'DELETE') THEN
      row = OLD;
    ELSE
      row = NEW;
    END IF;

    output = 'Basics Start-' || 'OPERATION = ' || TG_OP || ' and ID = ' || row.user_id || '-Basics End';

    output = output || 'Tutor Details Start-' || row.tutor_first_name || '-' ||
    row.tutor_last_name || '-' || row.tutor_phone_number || '-' || row.tutor_email|| '-' || row.is_active || '-Tutor Details End';

    PERFORM pg_notify('tutor_table_changed',output);

    -- Returning null because it is an after trigger.
    RETURN NULL;
    END;
   $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tutor_table_trigger ON tutor; CREATE TRIGGER tutor_table_trigger AFTER update on tutor for each row execute procedure tutor_table_trigger();
--DROP TRIGGER IF EXISTS tutor_table_trigger ON tutor; CREATE TRIGGER tutor_table_trigger AFTER insert or update or delete on tutor for each row execute procedure tutor_table_trigger();

"""


lead_table_trigger_text = """
CREATE OR REPLACE FUNCTION lead_table_trigger() RETURNS trigger AS $$
   DECLARE
    row RECORD;
    output TEXT;

    BEGIN
    -- Checking the Operation Type
    IF (TG_OP = 'DELETE') THEN
      row = OLD;
    ELSE
      row = NEW;
    END IF;

    output = 'Basics Start-' || 'OPERATION = ' || TG_OP || ' and ID = ' || row.lead_id || '-Basics End';

    output = output || 'Lead Details Start-' || row.lead_name || '-' || row.lead_phone_number || '-' || row.lead_email|| '-' || '-Lead Details End';

    PERFORM pg_notify('lead_table_changed',output);

    -- Returning null because it is an after trigger.
    RETURN NULL;
    END;
   $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS lead_table_trigger ON lead; CREATE TRIGGER lead_table_trigger AFTER update on lead for each row execute procedure lead_table_trigger();
--DROP TRIGGER IF EXISTS lead_table_trigger ON lead; CREATE TRIGGER lead_table_trigger AFTER insert or update or delete on lead for each row execute procedure lead_table_trigger();

"""


prospect_table_trigger_text = """
CREATE OR REPLACE FUNCTION prospect_table_trigger() RETURNS trigger AS $$
   DECLARE
    row RECORD;
    output TEXT;

    BEGIN
    -- Checking the Operation Type
    IF (TG_OP = 'DELETE') THEN
      row = OLD;
    ELSE
      row = NEW;
    END IF;

    output = 'Basics Start-' || 'OPERATION = ' || TG_OP || ' and ID = ' || row.prospect_id || '-Basics End';

    output = output || 'Prospect Details Start-' || row.prospect_first_name || '-' ||
    row.prospect_last_name || '-' || row.prospect_phone_number || '-' || row.prospect_email|| '-' || '-Prospect Details End';

    PERFORM pg_notify('prospect_table_changed',output);

    -- Returning null because it is an after trigger.
    RETURN NULL;
    END;
   $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS prospect_table_trigger ON prospect; CREATE TRIGGER prospect_table_trigger AFTER update on prospect for each row execute procedure prospect_table_trigger();
--DROP TRIGGER IF EXISTS prospect_table_trigger ON prospect; CREATE TRIGGER prospect_table_trigger AFTER insert or update or delete on prospect for each row execute procedure prospect_table_trigger();

"""
