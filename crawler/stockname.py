from functools import lru_cache

import pandas as pd


@lru_cache(maxsize=None)
def load_stock_data():
    df = \
        pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0,
                     converters={'종목코드': str})[0]
    df = df[['종목코드', '회사명']]
    df = df.rename(columns={'종목코드': 'code', '회사명': 'name'})
    return df


@lru_cache(maxsize=None)
def get_stock_name_by_stock_code(market_code, stock_code):
    if market_code == 'KS':
        df = load_stock_data()
        search_option = df['code'] == stock_code
        matching_row = df[search_option]
        try:
            stock_name = matching_row.iloc[0]['name']
            return stock_name
        except IndexError:
            return "???"
    else:
        pass
        # TODO 다른 시장일 때도 불러오는 보편적인 방법 구현하기
        return ""


if __name__ == '__main__':
    print(get_stock_name_by_stock_code('005930'))
