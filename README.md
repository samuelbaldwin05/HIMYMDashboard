# HIMYMDashboard
This app is a dashboard created using the HoloViz Panel library that allows users to visualize data from the show How I Met Your Mother. Visualizations include histograms, scatterplots, bar charts, box plots, line plots, and sankeys, each only taking in the proper data types for the given plot. Data includes natural language processed data that measures which character spoke the most in a given episode, the sentiment of the episode, and the number of times the character Barney says one of his catch phrases. Additionally data includes air date, director, writer, US viewer counts, and IMDB ratings for each episode. 


## Files
himym_api -  api to retrieve the data

himym_dash - takes in data and creates graphs including calling the sankey file, showing with HoloViz Panel

sankey - seperate file to create sankey graph

## How to run
Download the files and data

Make sure you have panel installed

In a terminal in the directory, input: panel serve himym_dash
