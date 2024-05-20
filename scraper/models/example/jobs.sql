{{ config(materialized='table') }}

select * from {{source('source_db', 'jobs')}}


