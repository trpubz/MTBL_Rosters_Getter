# Rosters_Getter

## Description
  This app navigates to ESPN's Fantasy Baseball Roster page and pulls the .html down for scraping.  It then puts the data into rosters which are Team dictionary objects.
This app serves an "extract" function in an ETL pipeline.

## Dependencies
- MTBL - Lg_Manager_Getter is required to run before this execution to link team name and team abbreviation.
- The league ID
  -  Additionally, the ESPN league must be set to public

## Outputs
- rosters in a .json file for ingestion into a "Loading"/"Analytical" app.
