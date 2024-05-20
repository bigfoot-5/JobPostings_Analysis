
{{
  config(
    materialized='incremental',
    unique_key='id'
  )
}}

WITH source_data AS (
    SELECT
        job_id AS id,
        title,
        company,
        place,
        date_posted
    FROM
        {{ ref('jobs') }}
)

SELECT *
FROM source_data
{% if is_incremental() %}
WHERE id NOT IN (SELECT id FROM {{ this }})
{% endif %}
