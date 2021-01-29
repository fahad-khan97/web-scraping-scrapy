# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
import json
import time


class AirbnbSpider(scrapy.Spider):
    name = 'airbnb'
    allowed_domains = ['www.airbnb.com']
    timestamp = int(time.time())
    cookies = {
        '3fb5f301f': 'control',
        '66bf01231': 'control',
        'AMP_TOKEN': '%24NOT_FOUND',
        '__ssid': 'e908c63b6bb9a8a0663dd0394b7b10b',
        '_csrf_token': 'V4%24.airbnb.com%24xPMq8Y7Iu5Y%24C6veBngwzVAmZ1W7qcxPd-P2j1vjKZ4Cpj6e3qBp3P4%3D',
        '_ga': 'GA1.2.423427519.1551090995',
        '_gat': '1',
        '_gcl_au': '1.1.1412589089.1551090996',
        '_gid': 'GA1.2.812061343.1551601092',
        '_user_attributes': '%7B%22curr%22%3A%22USD%22%2C%22guest_exchange%22%3A1.0%2C%22device_profiling_session_id%22%3A%221551090990--4722f4f6f996ada0cd801e37%22%2C%22giftcard_profiling_session_id%22%3A%221551616914--ebd29d2de9523343329bb1c2%22%2C%22reservation_profiling_session_id%22%3A%221551616914--c2c27382eef485b775d31672%22%7D',
        'a46dc25ab': 'short_upsell',
        'bev': '1551090989_iy3Ez2XiUZX6abEP',
        'cbkp': '1',
        'cereal_exp': '8',
        'e34ba1aae': 'treatment',
        'e8de742fb': 'treatment',
        'f4b08f5ff': 'control',
        'flags': '0',
        'hyperloop_explore_exp_v2': '3',
        'jitney_client_session_created_at': timestamp,
        'jitney_client_session_id': '07927b1b-d615-48d9-8646-155d5622612f',
        'jitney_client_session_updated_at': timestamp,
        'sdid': ''
    }

    def start_requests(self):
        yield scrapy.Request(url='https://www.airbnb.com/api/v2/explore_tabs?_format=for_explore_search_web&_intents=p1&adults=0&auto_ib=false&children=0&client_session_id=144fa3ca-5a16-496a-b77b-80ca187796e8&currency=USD&experiences_per_grid=20&fetch_filters=true&guests=0&guidebooks_per_grid=20&has_zero_guest_treatment=true&infants=0&is_guided_search=true&is_new_cards_experiment=true&is_standard_search=true&items_per_grid=18&key=d306zoyjsyarp7ifhu67rjxn52tv0t20&locale=en&luxury_pre_launch=false&metadata_only=false&place_id=ChIJOwg_06VPwokRYv534QaPC8g&query={0}&query_understanding_enabled=true&refinement_paths%5B%5D=%2Frestaurants&satori_version=1.1.8&screen_size=small&selected_tab_id=restaurant_tab&show_groupings=true&supports_for_you_v3=true&timezone_offset=60&version=1.4.5'.format(self.city),
                             callback=self.parse_id, cookies=self.cookies)

    def parse_id(self, response):
        data = json.loads(response.body)
        try:
            restaurants = data.get('explore_tabs')[0].get(
                'sections')[1].get('point_of_interest_items')
        except:
            restaurants = data.get('explore_tabs')[0].get(
                'sections')[0].get('point_of_interest_items')

        if restaurants is None:
            raise CloseSpider('No restaurant is available in this city')

        for restaurant in restaurants:
            yield scrapy.Request(url='https://www.airbnb.com/api/v2/place_activities/{0}?key=d306zoyjsyarp7ifhu67rjxn52tv0t20&currency=USD&locale=en&_format=for_spa_activity_pdp_web'.format(restaurant.get('id')),
                                 callback=self.parse)

        pagination_metadata = data.get('explore_tabs')[
            0].get('pagination_metadata')

        if pagination_metadata.get('has_next_page'):
            items_offset = pagination_metadata.get('items_offset')
            section_offset = pagination_metadata.get('section_offset')
            yield scrapy.Request(url='https://www.airbnb.com/api/v2/explore_tabs?_format=for_explore_search_web&_intents=p1&adults=0&auto_ib=false&children=0&client_session_id=f61893bf-4c34-474f-828a-6d6ad62255aa&currency=USD&experiences_per_grid=20&federated_search_session_id=cd55be59-e830-48eb-af05-2ecf50529628&fetch_filters=true&guests=0&guidebooks_per_grid=20&has_zero_guest_treatment=true&infants=0&is_guided_search=true&is_new_cards_experiment=true&is_standard_search=true&items_offset={0}&items_per_grid=18&key=d306zoyjsyarp7ifhu67rjxn52tv0t20&locale=en&luxury_pre_launch=true&metadata_only=false&place_id=ChIJOwg_06VPwokRYv534QaPC8g&query={2}%2C%20NY%2C%20United%20States&query_understanding_enabled=true&refinement_paths%5B%5D=%2Frestaurants&satori_version=1.1.8&screen_size=small&section_offset={1}&show_groupings=true&supports_for_you_v3=true&tab_id=restaurant_tab&timezone_offset=60&version=1.4.5'.format(items_offset, section_offset, self.city),
                                 callback=self.parse_id, cookies=self.cookies)

    def parse(self, response):
        restaurant = json.loads(response.body).get('place_activity')
        yield {
            'id':  restaurant.get('id'),
            'title':  restaurant.get('title'),
            'type':  restaurant.get('action_kicker'),
            'decription':  restaurant.get('description'),
            'place': {
                'address':  restaurant.get('place').get('address'),
                'city':  restaurant.get('place').get('city'),
                'country':  restaurant.get('place').get('country'),
                'latitude': restaurant.get('place').get('lat'),
                'longitude': restaurant.get('place').get('lng')
            },
            'phone_number':  restaurant.get('place').get('phone'),
            'website': restaurant.get('place').get('website'),
        }
