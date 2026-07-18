# Australia's Labour Market: Wages, Work, and Regional Inequality

An interactive data visualisation examining nearly three decades of the Australian labour market, built to answer a question with real relevance to household living standards: has pay kept up with work?

**Live visualisation:** https://arnob306.github.io/Australian-Labour-Market-Visualisation-/

## Why This Project

Australia went through two recessions, a pandemic, and a decade where unemployment kept falling but wages barely moved. That disconnect, often called wage decoupling, is one of the defining puzzles in the modern Australian economy, and it directly affects household income, regional opportunity, and economic policy. I built this project to trace that story clearly, using real government data rather than summary headlines, and to make it understandable to a general audience with no assumed background in economics or statistics.

## Key Findings

- Unemployment fell steadily from 5.8 percent in 2012 to 5 percent by 2019, yet wage growth stayed flat near 2 percent, well below its historical range of 3 to 4 percent
- The part time share of employment grew from under 28 percent in 1997 to above 32 percent by the mid 2010s, shifting the overall bargaining position of the workforce
- Unemployment reached 7.5 percent in July 2020, the largest peacetime labour market shock in the dataset, followed by an unusually rapid recovery
- Regional unemployment varies enormously beneath the national average, with some Sydney suburbs recording unemployment counts around three times higher than others in the same city
- The analysis tracks 87 separate regions across the full 1997 to 2025 period

## What's Inside

The visualisation is structured as a five part narrative, moving from the national picture down to the regional level.

1. **National Overview.** The thirty year relationship between unemployment and wage growth, and where that relationship broke down.
2. **Structural Change.** The long term shift toward part time and casual employment, and what that means for worker bargaining power.
3. **Wage Stagnation.** Where productivity gains went if not into wages, plus a look at the mismatch between job vacancies and unemployment.
4. **Regional Inequality.** A choropleth map of unemployment across 87 regions, showing how much national averages can hide.
5. **Economic Shocks.** A full cycle view spanning the GFC, the wage stagnation decade, and the COVID shock, including a combined stress index across all indicators.

## Data Sources

- RBA Table H5, Labour Force data sourced from the ABS, monthly figures from 1978 to 2025
- RBA Table H4, Labour Costs and Productivity data from the ABS, quarterly figures from 1997 to 2025
- ABS MRM1, SA4 Modelled Unemployment Estimates, monthly figures from 2012 to 2025

## Technical Approach

The visualisation is built with Vega-Lite and Vega-Embed, using layered charts to combine time series data, a geographic choropleth, and a normalised heatmap within one coherent narrative. Regional boundaries were sourced as ABS ASGS 2021 shapefiles and converted to TopoJSON using Mapshaper. Raw RBA data was reformatted into ISO 8601 dates, and SA4 level data was reshaped from wide to long format using pandas.

One of the harder problems was getting multi layer charts to render correctly. Vega-Lite resolves axis scales across all layers by default, which meant annotation layers were distorting the true range of the underlying data. The fix was to restrict scale domain settings to the primary data layers only, and to position annotation layers using fixed pixel values instead of letting them share the data scale.

## Tech Stack

Vega-Lite 5, Vega-Embed 6, Python (pandas), Mapshaper
