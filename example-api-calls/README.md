# Example API Calls

This example script contains several requests to showcase how to interact with the  pixolution Flow API. This is a great starting point to for your own developments as the script is as barebone as possible.

### Requirements
To run this example you have the pixolution Flow docker image up and running and have a terminal with the Python virtual environment activated.
Follow the steps described in the [README.md](../) in project root.


## Usage

This description is quite short, because the python code explains itself.
Learn how to:
 * Init the image collection ([API docs](https://docs.pixolution.org/#/installation?id=initial-start))
 * Add a document to the collection ([API docs](https://docs.pixolution.org/#/data-indexing))
 * Search by keywords using wildcard query
 * Search by document id
 * Search by random web image ([API docs](https://docs.pixolution.org/#/visual-search?id=search-by-url))
 * Search by color ([API docs](https://docs.pixolution.org/#/visual-search?id=search-by-color))
 * Scan for duplicate images with a sample image ([API docs](https://docs.pixolution.org/#/duplicate-detection))

Simply run the following script to trigger the various requests and see their output.

```bash
python send_api_requests.py
```
