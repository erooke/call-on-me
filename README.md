
## Dependencies

* Python >= 3.12
* [fswatch](https://github.com/emcrisostomo/fswatch?tab=readme-ov-file#getting-fswatch)
* Probably other stuff idk

## Developing locally

Create a local Python environment:

```sh
$ python3.12 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Run the site generator, which will produce a bunch of files in the `out/` directory:

```shell
$ python main.py
```

To have the site rebuild and serve automatically, open two different terminal windows.
In the first, run:

```shell
$ source venv/bin/activate
$ ./bin/watch.sh
```

In the second terminal:

```shell
$ source venv/bin/activate
$ ./bin/serve.sh
```

The serve script will print `localhost:$PORT`; open that in a browser and you will see the site.

Any file change will trigger a rebuild, which takes a few seconds.
When the rebuild completes, you can refresh the page and see the changes reflected.
If you add new files that you want to watch, you might have to restart the watch process.