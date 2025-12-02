<script setup lang="ts">
import { onMounted, watch, ref } from 'vue';
import L from 'leaflet';
import type { GeoJsonFeature, LineSection, TrainLog } from '../types';
import { DEFAULT_STYLE, HIGHLIGHT_STYLE, DIMMED_STYLE } from './MapParams';

const props = defineProps<{
  features: GeoJsonFeature[];
  selectedLogId: string | null;
}>();

const mapContainer = ref<HTMLElement | null>(null);
let map: L.Map | null = null;
let geoJsonLayer: L.GeoJSON | null = null;
let highlightLayer: L.GeoJSON | null = null;

const buildLogKey = (log: TrainLog) =>
  `${log.serial}-${log.departure_day}-${log.departure_station}`;

const collectStationOrder = (sections: LineSection[]) => {
  const order: string[] = [];
  sections.forEach((section, index) => {
    if (index === 0) {
      order.push(section.between.start);
    }
    order.push(section.between.end);
  });
  return order;
};

const normalizeStationName = (name: string) =>
  name.replace(/（.*?）|\(.*?\)/g, '').trim();

const findStationIndex = (stationOrder: string[], stationName: string) => {
  const normalizedTarget = normalizeStationName(stationName);
  return stationOrder.findIndex(candidate => {
    if (candidate === stationName) return true;
    const normalizedCandidate = normalizeStationName(candidate);
    return (
      normalizedCandidate === normalizedTarget ||
      normalizedCandidate.includes(normalizedTarget) ||
      normalizedTarget.includes(normalizedCandidate)
    );
  });
};

const pickSectionsForRide = (sections: LineSection[] = [], ride: TrainLog) => {
  if (!sections.length) return [] as LineSection[];
  const stationOrder = collectStationOrder(sections);
  const startIndex = findStationIndex(stationOrder, ride.departure_station);
  const endIndex = findStationIndex(stationOrder, ride.arrival_station);

  if (startIndex === -1 && endIndex === -1) {
    return [] as LineSection[];
  }

  if (startIndex !== -1 && endIndex !== -1) {
    if (startIndex === endIndex) {
      const sectionIndex = Math.min(startIndex, sections.length - 1);
      return sections[sectionIndex] ? [sections[sectionIndex]] : [];
    }
    const lower = Math.min(startIndex, endIndex);
    const upper = Math.max(startIndex, endIndex);
    const slice = sections.filter((_, idx) => idx >= lower && idx < upper);
    return startIndex <= endIndex ? slice : slice.slice().reverse();
  }

  if (startIndex !== -1) {
    return sections.slice(startIndex);
  }

  return sections.slice(0, endIndex);
};

const clearHighlightLayer = () => {
  if (highlightLayer && map) {
    highlightLayer.remove();
    highlightLayer = null;
  }
};

const resetAllStyles = () => {
  if (!geoJsonLayer) return;
  geoJsonLayer.eachLayer((layer: any) => {
    layer.setStyle(DEFAULT_STYLE);
  });
};

const renderFeatures = () => {
  if (!map) return;

  if (geoJsonLayer) {
    geoJsonLayer.remove();
    geoJsonLayer = null;
  }

  clearHighlightLayer();

  if (!props.features || !props.features.length) {
    return;
  }

  geoJsonLayer = L.geoJSON(props.features as any, {
    style: () => DEFAULT_STYLE,
    onEachFeature: (feature, layer) => {
      if (feature.properties && feature.properties.line_name) {
        layer.bindTooltip(feature.properties.line_name);
      }
    }
  }).addTo(map);

  const bounds = geoJsonLayer.getBounds();
  if (bounds.isValid()) {
    map.fitBounds(bounds);
  }
};

const applySelection = (newId: string | null) => {
  if (!geoJsonLayer) {
    if (!newId) {
      clearHighlightLayer();
    }
    return;
  }

  if (!newId) {
    clearHighlightLayer();
    resetAllStyles();
    return;
  }

  let sectionsToHighlight: LineSection[] = [];
  let fallbackSections: LineSection[] = [];

  geoJsonLayer.eachLayer((layer: any) => {
    const feature = layer.feature as GeoJsonFeature;
    const rides = feature.properties.rides || [];
    const matchedRide = rides.find(log => buildLogKey(log) === newId);

    if (matchedRide) {
      layer.setStyle(DEFAULT_STYLE);
      if (!sectionsToHighlight.length) {
        sectionsToHighlight = pickSectionsForRide(feature.properties.sections || [], matchedRide);
      }
      if (!fallbackSections.length) {
        fallbackSections = feature.properties.sections || [];
      }
    } else {
      layer.setStyle(DIMMED_STYLE);
    }
  });

  if (!sectionsToHighlight.length && fallbackSections.length) {
    sectionsToHighlight = fallbackSections;
  }

  clearHighlightLayer();

  if (!sectionsToHighlight.length || !map) {
    return;
  }

  const featureCollection = {
    type: 'FeatureCollection',
    features: sectionsToHighlight.map(section => ({
      type: 'Feature',
      properties: { sequence: section.sequence },
      geometry: section.geometry,
    })),
  } as any;

  highlightLayer = L.geoJSON(featureCollection, {
    style: () => HIGHLIGHT_STYLE,
  }).addTo(map);

  highlightLayer.bringToFront();
};

// 地図の初期化
onMounted(() => {
  if (!mapContainer.value) return;

  // 1. 地図インスタンス作成
  map = L.map(mapContainer.value).setView([36.5, 139.5], 8);

  // 2. OpenStreetMapのタイルを追加
  L.tileLayer(import.meta.env.VITE_OSM_TILE_URL, {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18,
  }).addTo(map);

  renderFeatures();
});

// 選択されたログが変わった時の処理
watch(() => props.selectedLogId, (newId) => {
  applySelection(newId);
});

watch(() => props.features, () => {
  renderFeatures();
  applySelection(props.selectedLogId);
}, { deep: true });
</script>

<template>
  <div ref="mapContainer" class="w-full h-full z-0"></div>
</template>
