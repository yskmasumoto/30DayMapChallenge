import { ref, computed, onMounted } from 'vue';
import type { GeoJsonFeature, RailroadFeatureCollection, TrainLog } from '../types';

const dataset = ref<RailroadFeatureCollection | null>(null);
let loadingPromise: Promise<void> | null = null;

const ensureDataset = async () => {
  if (dataset.value) return;
  if (!loadingPromise) {
    loadingPromise = fetch(import.meta.env.VITE_RAILROAD_DATA_URL)
      .then(res => res.json())
      .then((json) => {
        dataset.value = json as RailroadFeatureCollection;
      })
      .finally(() => {
        loadingPromise = null;
      });
  }
  await loadingPromise;
};

export function useRailroadData() {
  // 生データ
  const features = ref<GeoJsonFeature[]>(dataset.value?.features ?? []);

  onMounted(async () => {
    await ensureDataset();
    features.value = dataset.value?.features ?? [];
  });

  // 選択されたログID
  const selectedLogId = ref<string | null>(null);

  // 重複を除いたユニークなログリストを作成
  const uniqueLogs = computed(() => {
    const logMap = new Map<string, TrainLog>();

    for (const feature of features.value) {
      const rides = feature.properties.rides ?? [];
      if (rides.length) {
        for (const log of rides) {
          // ユニークキーの生成 (シリアル番号 + 日付 + 出発駅)
          const key = `${log.serial}-${log.departure_day}-${log.departure_station}`;
          if (!logMap.has(key)) {
            logMap.set(key, { ...log, uniqueId: key });
          }
        }
      }
    }
    // 日付順などにソートしても良い
    return Array.from(logMap.values());
  });

  // ログを選択する関数
  const selectLog = (id: string) => {
    selectedLogId.value = selectedLogId.value === id ? null : id; // トグル
  };

  return {
    features,
    uniqueLogs,
    selectedLogId,
    selectLog
  };
}
