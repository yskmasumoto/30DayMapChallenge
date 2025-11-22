from dataclasses import dataclass
from typing import List


@dataclass
class Country:
    """
    国情報
    name: 国名
    color: 国土の色
    """

    name: str
    color: str


@dataclass
class Config:
    """
    マップに描画する際の設定
    title: グラフタイトル
    fig_size: 図のサイズ
    xlim: x軸（経度方向）の範囲
    ylim: y軸（緯度方向）の範囲
    xticks: x軸の目盛り
    yticks: y軸の目盛り
    countries: 国情報のリスト・名称はnameで、その他の設定も含む
    output: 出力ファイル名
    """

    title: str
    fig_size: List[int]
    xlim: List[float]
    ylim: List[float]
    xticks: List[float]
    yticks: List[float]
    countries: List[Country]
    output: str

    def __post_init__(self):
        # countriesがDictのリストで渡された場合に対応
        self.countries = [
            Country(**country) if isinstance(country, dict) else country
            for country in self.countries
        ]
