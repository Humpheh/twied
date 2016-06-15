Guide
=====

Installation
------------

Below is a guide on how to setup and use the package. This package required *Python 3*. A number of other
modules are required for the module to function correctly. Installing the module using *pip* should automatically
include all of these modules, however they may need to be retrieved seperately.

Required modules and supported versions can be seen here: `<https://github.com/Humpheh/twied/blob/master/requirements.txt>`_.

**Pip Installation:**

`twied` can be installed via pip:

.. code-block:: bash

    pip install git+https://github.com/Humpheh/twied.git

**Source Code:**

The source code for `twied` can be retrieved from *GitHub* `<https://github.com/Humpheh/twied>`_. This can
be cloned using:

.. code-block:: bash

    git clone https://github.com/Humpheh/twied.git

**Example Scripts:**

Example usage scripts can be seen in the *GitHub* repository under the directory `/scripts/examples`.

Usage
-----

MI Configuration
~~~~~~~~~~~~~~~~

Below is a basic breakdown of how setting up for using the MI implementation would work:

    1. Obtain the `twied` package.
    2. Install prerequisite modules (*pip* likely will install them for you).
    3. Download databases (see below for link).
    4. Setup config file.
    5. Create inference script.
    6. Start inference.

Below is an example config file for use with the :class:`twied.multiind.inference.InferThread`
class. Each of the sections is broken down below the example.

.. code-block:: ini

    [twitter]
    app_key = wYHFS6G9fqVNxYwt53UNUcxT0
    app_secret = MU3r4yi2HGDrAbBma2syPpOvFOcWFxaUIiKmeySX8Ard80lr53
    oauth_token = 3950426785-SNgK3NmghSzdjLcJGRTAwQq3xyMait0bVQ6HVvV
    oauth_token_secret = x0FASasjEHqsSvLAZ3h6sqClPWtt54TcM78W8PLOJ1BLv

    [mongo]
    address = localhost
    port = 27017
    database = twitter
    collection = tweets

    #### Settings for Multi-Indicator Approach ####

    [multiindicator]
    workers = 10
    gadm_polydb_path = D:/ds/polydb_2.db
    tld_csv = D:/ds/tlds.csv

    [mi_weights]
    TAG = 10
    COD = 2.72
    GN = 1.51
    GN_1 = 2.01
    GN_2 = 1.96
    GN_3 = 1.96
    SP = 0.67
    LBS = 4.26
    TZ = 0.56
    WS_1 = 1.07

    [geonames]
    url = api.geonames.org
    user = humph
    limit = 5
    fuzzy = 0.8

    [dbpedia]
    spotlight_url = spotlight.sztaki.hu
    spotlight_port = 2222
    spotlight_page = /rest/annotate

    [slinf]
    min_mentions = 3
    # 4
    max_depth = 3
    req_locations = 1
    max_iterations = 4
    num_timelines = 2

**Fields:**
    - **twitter** - This section contains the settings for the Twitter API.
      These settings are not directly used by the Inference class, so can be omitted.
    - **mongo** - This section contains the connection information for the MongoDB,
      including the location of the database, and the database and table names to infer the tweets from.
    - **multiindicator** - The *workers* value is an integer value of the number of
      simultaneous inference threads to run concurrently. The *gadm_polydb_path* is the location of the polygon
      database (see below) and the *tld_csv* string is the location of the TLD to country name file (see below).
    - **mi_weights** - This contains the weights of each of the indicators. The default
      values in this config are the values lifted from the original paper.

        :`TAG`: weight of geotag indicator
        :`COD`: weight of coordinate indicator
        :`GN`: weight of default geonames indicator
        :`GN_1`: weight of geonames indicator when string split by '/'
        :`GN_2`: weight of geonames indicator when string split by '-'
        :`GN_3`: weight of geonames indicator when backup message indicator is used
        :`SP`: weight of message indicator
        :`LBS`: weight of location based services indicator (not implemented)
        :`TZ`: weight of both timezone indicators
        :`WS_1`: weight of TLD indicator

    - **geonames** - This contains settings for connecting to the geonames API. *limit* is the max
      number of suggestions to return and *fuzzy* is the search fuzzy-ness parameter.
    - **dbpedia** - This contains settings for the URL of the DBPedia spotlight interface.
    - **slinf** - This can be omitted. Containted settings for the spatial label propagation method.

**Files:**
    The MI approach uses two main extra databases, the *polygon database* and the
    *tld* database. These are compiled from various sources. Precompiled database
    files can be downloaded here: https://drive.google.com/open?id=0B0xoZYJ_Tg1aYVhvNTRlRGRiLW8
