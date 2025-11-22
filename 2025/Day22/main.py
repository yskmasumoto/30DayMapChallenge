import json
import os
from typing import Any, Dict, List

import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe  # エフェクト用
import matplotlib.pyplot as plt
import rasterio
from models import Config
from rasterio.plot import show


def create_map(cfg: Config):
    # ---------------------------------------------------------
    # 1. 環境変数からパスを取得
    # ---------------------------------------------------------
    try:
        path_countries = os.environ["PATH_COUNTRIES"]
        path_disputed = os.environ["PATH_DISPUTED"]
        path_lakes = os.environ["PATH_LAKES"]
        path_rivers = os.environ["PATH_RIVERS"]
        path_raster = os.environ["PATH_RASTER"]
    except KeyError as e:
        print(f"エラー: 環境変数 {e} が設定されていません。")
        return

    # ---------------------------------------------------------
    # 2. ベクターデータの読み込み
    # ---------------------------------------------------------
    print("ベクターデータをロード中...")
    gdf_countries = gpd.read_file(path_countries)
    gdf_disputed = gpd.read_file(path_disputed)
    gdf_lakes = gpd.read_file(path_lakes)
    gdf_rivers = gpd.read_file(path_rivers)

    # ---------------------------------------------------------
    # 3. プロットの準備
    # ---------------------------------------------------------
    _, ax = plt.subplots(figsize=(cfg.fig_size))
    ax.set_facecolor("#1a1a1a")  # 背景色

    # ---------------------------------------------------------
    # 4. ラスターデータの描画
    # ---------------------------------------------------------
    print("ラスターデータをロード中...")
    with rasterio.open(path_raster) as src:
        # グレースケールのラスターデータ
        show(src, ax=ax, zorder=0, interpolation="bilinear", cmap="gray", alpha=0.6)

    # ---------------------------------------------------------
    # 5. ベクターレイヤーの描画
    # ---------------------------------------------------------
    # (1) 国境線と国土
    for info in cfg.countries:
        country = info.name
        gdf_country = gdf_countries[gdf_countries["NAME"] == country]
        gdf_country.plot(
            ax=ax,
            facecolor=info.color,
            edgecolor="white",
            linewidth=0.5,
            linestyle=":",
            alpha=0.3,
            zorder=1,
        )

    # (2) 湖
    lakes_effect = [pe.SimpleLineShadow(alpha=0.2, offset=(1, -1)), pe.Normal()]
    gdf_lakes.plot(
        ax=ax,
        color="cyan",
        edgecolor="cyan",
        alpha=0.7,
        zorder=2,
        path_effects=lakes_effect,
    )

    # (3) 河川 (ネオン発光)
    rivers_effect = [
        pe.Stroke(linewidth=4, foreground="cyan", alpha=0.4),
        pe.Normal(),
    ]
    gdf_rivers.plot(
        ax=ax,
        color="#8cffff",  # 河川のラインの芯の色
        linewidth=0.8,
        zorder=3,
        path_effects=rivers_effect,
    )

    # (4) 紛争地帯
    disputed_effect = [
        pe.Stroke(linewidth=3, foreground="black", alpha=0.5),
        pe.Normal(),
    ]
    gdf_disputed.plot(
        ax=ax,
        facecolor="none",
        edgecolor="#ff3366",
        hatch="///",
        linewidth=1.5,
        zorder=4,
        path_effects=disputed_effect,
    )

    # ---------------------------------------------------------
    # 6. 特定範囲へのフォーカス
    # ---------------------------------------------------------
    ax.set_xlim(cfg.xlim[0], cfg.xlim[1])
    ax.set_ylim(cfg.ylim[0], cfg.ylim[1])

    # ---------------------------------------------------------
    # 7. 見た目の調整
    # ---------------------------------------------------------
    # タイトル設定 (フォントがあれば指定したいが、なければサイズと色で勝負)
    plt.title(
        cfg.title,
        fontsize=18,
        pad=20,
        color="white",  # 背景が黒なので白文字
        fontweight="bold",
    )

    # 軸ラベル削除 (コンフィグで空リスト指定されていますが、念のため非表示設定)
    ax.set_xticks(cfg.xticks)
    ax.set_yticks(cfg.yticks)

    # 凡例設定
    legend_patches = [
        mpatches.Patch(
            facecolor="none", edgecolor="white", linestyle=":", label="Border"
        ),
        mpatches.Patch(color="cyan", label="Lakes/Rivers"),  # まとめてしまいました
        mpatches.Patch(
            facecolor="none", edgecolor="#ff3366", hatch="///", label="Disputed Areas"
        ),
    ]

    first_legend = plt.legend(
        handles=legend_patches,
        loc="upper right",
        fontsize=10,
        framealpha=0.9,  # 少し不透明度を上げる
        facecolor="#333333",  # 凡例ボックスの背景色
        edgecolor="none",
        labelcolor="white",
        title="Features",
        title_fontsize=12,
    )
    # タイトルの色も白にする
    plt.setp(first_legend.get_title(), color="white")
    ax.add_artist(first_legend)

    country_legend_patches = [
        mpatches.Patch(color=info.color, label=info.name) for info in cfg.countries
    ]
    second_legend = plt.legend(
        handles=country_legend_patches,
        loc="lower left",
        fontsize=10,
        framealpha=0.9,
        facecolor="#333333",
        edgecolor="none",
        labelcolor="white",
        title="Countries",
        title_fontsize=12,
    )
    plt.setp(second_legend.get_title(), color="white")

    # ---------------------------------------------------------
    # 8. 保存
    # ---------------------------------------------------------
    # facecolorを指定して、図の外側の余白も黒くする
    plt.savefig(cfg.output, dpi=300, bbox_inches="tight", facecolor="#1a1a1a")
    print(f"地図を保存しました: {cfg.output}")


if __name__ == "__main__":
    with open("config/config.json", "r") as f:
        cfg_json: List[Dict[str, Any]] = json.load(f)

    cfgs = []
    for cfg_dict in cfg_json:
        cfgs.append(Config(**cfg_dict))

    for cfg in cfgs:
        create_map(cfg)
