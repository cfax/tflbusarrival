from utilities import Utilities as U


class TflApi(object):
    __base_url = 'http://countdown.api.tfl.gov.uk/interfaces/ura/instant_V1?'

    def getStopList(self, lat, lon):
        """Return list of bus stops (type: STBC) around the user's location"""

        radius = str(300)
        return_list = [
            'StopPointName',
            'StopCode1',
            'Bearing',
            'StopPointIndicator',
            'Latitude',
            'Longitude'
        ]

        query = 'Circle={lat},{lon}'.format(lat=lat, lon=lon) + ',' + \
                radius + ',' + \
                '&StopPointState=0&StopPointType=STBC' + \
                '&ReturnList=' + ','.join(return_list)
        url = self.__base_url + query
        response = U.url_open(url, 'Error retrieving list of stops')

        timestamp = response.readline()
        result = response.readlines()

        stops = []
        for r in result:
            # Clean entry and split into a list
            r = r.rstrip().strip('[]').split(',')
            # Discard first element (always 0) and replace any leading/trailing double quotes
            r = [i.strip('"') for i in r[1:]]
            stops.append(dict(zip(return_list, r)))

        # stopcode_list = [s['StopCode1'] for s in stops]
        return stops

    def getBusList(self, stopcode_list):
        """Return list of busses stops (type: STBC) around the user's location"""

        return_list = [
            'StopPointName',
            'StopCode1',
            'LineName',
            'DestinationText',
            'EstimatedTime',
        ]

        stops = ','.join(stopcode_list)
        query = 'StopCode1={}'.format(stops) + \
                '&VisitNumber=1' + \
                '&ReturnList=' + ','.join(return_list)

        url = self.__base_url + query
        response = U.url_open(url, 'Error retrieving list of busses')

        timestamp = response.readline()
        result = response.readlines()

        busses = []
        for r in result:
            # Clean entry and split into a list
            r = r.rstrip().strip('[]').split(',')
            # Discard first element (always 1) and replace any leading/trailing double quotes
            r = [i.strip('"') for i in r[1:]]
            # Convert epoch time to readable format
            r = r[:-1] + [U.epoch_to_localtime(r[-1])]
            busses.append(dict(zip(return_list, r)))

        return busses
