# Introduction
This project aims to scrape data from linkedin job postings and return the following information:
* The company
* Job role
* Date Posted
* Location
* The list of skills requred for the role

To get the list of key skills from the scraped Job description, the project uses Llama3 model using Langchain and Ollama libraries

- - - - 

# Running the code
After cloning the repository run the following commands to start the containers.

`docker compose build`

`docker compose up -d`

After the containers are up and running we use Airflow to run the containers.
Go to `localhost:8080` on your Web browser. Then run the Directed Acyclic Graph that is available.
After the DAG is run successfully, all the information regarding each of the jobs will become available in the form of a CSV file.

- - - - 
