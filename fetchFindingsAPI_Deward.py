import requests
import time
import pandas as pd


def get_data():
    """
    Fetch data from source using provided API
    :return: list of dictionaries
    """

    # Load auth keys
    with open('auth.txt') as f:
        auth = f.readlines()
    token = auth[0].replace('\n', '')
    orgID = auth[1].replace('\n', '')
    appID = auth[2].replace('\n', '')

    # Construct urls and variables
    urls = [f'https://www.shiftleft.io/api/v4/orgs/{orgID}/apps/{appID}/findings']
    headers = {"Authorization": f'Bearer {token}'}
    counter = 1
    data_list = []

    # Loop through base url and 'next_page' url and save data to list
    for url in urls:
        print(f'Sending request: {counter}')
        response = requests.get(url, headers=headers).json()
        findings = response['response']['findings']
        print('Extracting data from response...')
        for finding in findings:
            data = {}
            for tag in finding['tags']:
                data[tag['key']] = tag['value']
            data_list.append(data)
        print('Done.')

        # If there is 'next_page' then append the 'next_page' url to list of urls
        if 'next_page' in response:
            urls.append(response['next_page'])
            counter += 1
            print('Getting next page... \n')
        else:
            print('Last request.')
        time.sleep(2)

    return data_list


def get_data_frame(data) -> pd.DataFrame:
    """
    Get data_list and convert to data frame
    :param data: list of dictionaries
    :return: DataFrame
    """

    # Convert list of data to dataFrame and return DataFrame
    df = pd.DataFrame(data)

    # Extract wanted tags
    df = df[['category', 'sink_method', 'source_method']]
    return df


if __name__ == '__main__':
    data = get_data()
    df = get_data_frame(data)

    # Top 5 Sink methods with findings counts:
    print('\n Top 5 sink methods with finding count:')
    sink_df = pd.DataFrame(df.sink_method.value_counts().nlargest(5))
    sink_df = sink_df.rename(columns={'sink_method': 'findings_count'}).reset_index().rename(
        columns={'index': 'sink_method'})
    print(sink_df)

    # Top 5 source methods with categories and findings counts:
    source_df = pd.DataFrame(df.groupby(['category']).source_method.value_counts().nlargest(5))
    source_df = source_df.rename(columns={'source_method': 'findings_count'}).reset_index()
    print('\n Top 5 source methods with categories and finding count:')
    print(source_df)
