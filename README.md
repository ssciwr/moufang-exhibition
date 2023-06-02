# Franz Moufang - The Social Network

This is a network visualization based on `dash-cytoscape` for the art exhibition [THE SOCIAL NETWORK. Die Gästebücher des Kunstsammlers Franz Moufang](https://www.uni-heidelberg.de/de/veranstaltungen/the-social-network-die-gaestebuecher-des-kunstsammlers-franz-moufang-2023-06-09) in the Kunstverein Heidelberg.

## How to install and run

The web app needs to be served locally or over the internet.

Requirements:
* Python + Pip

Instructions:

```bash
python -m pip install -r requirements.txt
python app.py
```

If you need to serve this in the production environment, you should stop the previously running
`gunicorn` process by identifying its PID with `ps ax | grep gunicorn` and `kill` it. Then, in
the `moufang-exhibition` directory do:

```bash
nohup gunicorn app:server -b :8000 &
```

## License

The code in `app.py` is licensed under the MIT license. The data in `data.json` is licensed t.b.d.
