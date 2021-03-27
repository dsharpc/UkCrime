# UK Crime Dashboard

Visualising Crime statistics in England using Streamlit and the Police API.

## Preview 

Take a look at this dashboard [here](http://ukcrime.danielsharp.me).

You can also directly pull the docker image from [Docker Hub](https://hub.docker.com/r/dsharpc/ukcrime).

## Running locally

Build the Docker image with the following command:
```
docker build -t ukcrime .
```

Run the container:
```
docker run -d -p 8501:8501 -v $PWD/app:/app ukcrime
```

The streamlit site should be available on:
```
localhost:8501
```

## Development

To develop and add new features to the site, you can modify the sctipts in the app folder, where app.py is the what loads initially and is mainly made up of the widgets on the sidebar, while overview.py and trends.py are each of the pages.

