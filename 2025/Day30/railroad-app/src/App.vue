<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRailroadData } from './composables/useRailroadData';
import MapView from './components/MapView.vue';
import LogCard from './components/LogCard.vue';
import type { TrainLog } from './types';

const { features, uniqueLogs, selectedLogId, selectLog } = useRailroadData();

type SortOption = 'recent' | 'oldest' | 'line';
const sortOption = ref<SortOption>('recent');

const departureTimestamp = (log: TrainLog) => {
  const day = log.departure_day || '1970-01-01';
  const time = log.departure_date || '00:00';
  const value = Date.parse(`${day}T${time}`);
  return Number.isNaN(value) ? 0 : value;
};

const sortedLogs = computed(() => {
  const logs = [...uniqueLogs.value];
  switch (sortOption.value) {
    case 'oldest':
      return logs.sort((a, b) => departureTimestamp(a) - departureTimestamp(b));
    case 'line':
      return logs.sort((a, b) => a.line.localeCompare(b.line, 'ja'));
    case 'recent':
    default:
      return logs.sort((a, b) => departureTimestamp(b) - departureTimestamp(a));
  }
});
</script>

<template>
  <div class="flex h-screen w-screen overflow-hidden bg-gray-100">
    <div class="w-1/2 h-full relative border-r border-gray-300 shadow-lg z-10">
      <MapView
        :features="features"
        :selected-log-id="selectedLogId"
      />

      <div class="absolute top-4 left-14 bg-white/90 p-2 rounded shadow backdrop-blur-sm z-[1000]">
        <h1 class="text-xl font-bold text-gray-800">Railroad Visualizer</h1>
        <p class="text-xs text-gray-600">Select a trip to highlight the route</p>
      </div>
    </div>

    <div class="w-1/2 h-full overflow-y-auto p-4 bg-gray-50">
      <div class="max-w-2xl mx-auto">
        <div class="flex flex-wrap gap-4 justify-between items-center mb-4 sticky top-0 bg-gray-50 py-2 z-10">
          <h2 class="text-xl font-semibold text-gray-700">
            Travel Logs ({{ sortedLogs.length }})
          </h2>
          <div class="flex items-center gap-2 text-sm text-gray-600">
            <label for="sortOption">ソート:</label>
            <select id="sortOption"
                    v-model="sortOption"
                    class="border border-gray-300 rounded px-2 py-1 bg-white text-gray-700">
              <option value="recent">出発日 (新しい順)</option>
              <option value="oldest">出発日 (古い順)</option>
              <option value="line">路線名 (A→Z)</option>
            </select>
          </div>
          <span v-if="selectedLogId"
                @click="selectLog(selectedLogId)"
                class="text-sm text-blue-600 cursor-pointer hover:underline">
            Clear Selection
          </span>
        </div>

        <div class="space-y-2">
          <LogCard
            v-for="log in sortedLogs"
            :key="log.uniqueId"
            :log="log"
            :is-selected="selectedLogId === log.uniqueId"
            @click="selectLog"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* スクロールバーのカスタマイズ（任意） */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: #f1f1f1;
}
::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
