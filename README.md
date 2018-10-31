# pan-tort-source
This is the repository that supports the development and build of the pan-tort docker container.  The container is the end-user portion.  If you only want to **use** pan-tort (not develop it) then see https://github.com/PaloAltoNetworks/pan-tort and use the docker-compose file in that repository to download and run pan-tort.

If you do need to develop against pan-tort, this is the right repository.  Read on.

## Hash Search as part of the Testing Output Response Toolkit


## Install & start the hash search application
### 1. Clone repo
```git clone https://www.github.com/PaloAltoNetworks/pan-tort-source.git```
<br/>
### 2. Change into repo directory
```cd pan-tort-source```
<br/>
### 3. Create python 3.6 virtualenv
```python3.6 -m venv env```
<br/>
### 4. Activate virtualenv
```source env/bin/activate```
<br/>
### 5. Download required libraries
```pip install -r requirements.txt```
<br/>
### 6. Edit your ~/.panrc and put in your autofocus key then link the file
```
cd project
ln -s ~/.panrc
cd ..
```
<br/>

## From this point on, you must have at least elasticsearch (6.2 or greater) installed and Kibana, if you wish to use visualizations.
### 7. Load the ES mappings <br/>
```curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/hash-data/' -d @misc/hash-data-mappings.json```<br/>

### 8. Start the tort backend
```python ./pan-tort-api.py```
<br/>
### 10. Populate Kibana Dashboards
- Navigate to Kibana @ http://<your-ip>:5601 and go to Management -> Index Patters<br/>
- Create a new index pattern based on "hash-data" and select "query_time" for the time field<br/>
- Go to Managment -> Saved Objects and select Import<br/>
- Load each of the hash_data_*.json files in the misc directory (you will have to do it 3 times)<br/>
    - Use the hash-data index pattern of course<br/>

### 11. Goto http://<your-ip>:5061 to use the UI to load hashes. 



<br/>

<br/><br/>
## Best Practices and Optional Configuration
You should be all set.  For even more ideas on what you can do with the system and other things that you can download and install to get the most out of pan-tort, use the [pan-tort end user Wiki](https://github.com/PaloAltoNetworks/pan-tort/wiki/overview)
