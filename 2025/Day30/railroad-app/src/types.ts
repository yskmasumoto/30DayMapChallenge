export interface TrainLog {
  company: string;
  line: string;
  departure_station: string;
  departure_day: string;
  departure_date: string;
  arrival_station: string;
  arrival_day: string;
  arrival_date: string;
  serial: string;
  name: string;
  times: string;
  number: string;
  // フロントエンドでの識別用ID
  uniqueId?: string;
}

export interface DataYearRange {
  from: number;
  to: number;
}

export interface SectionEndpoint {
  start: string;
  end: string;
}

export interface SectionGeometry {
  type: string;
  coordinates: number[][];
}

export interface LineSection {
  sequence: number;
  between: SectionEndpoint;
  status: string;
  geometry: SectionGeometry;
}

export interface GeoJsonProperties {
  line_id: string;
  line_type_code: string;
  line_name: string;
  operator_name: string;
  opened_year: number | null;
  data_year: DataYearRange;
  sections: LineSection[];
  rides: TrainLog[];
  [key: string]: unknown;
}

export interface GeoJsonFeature {
  type: "Feature";
  properties: GeoJsonProperties;
  geometry: any;
}

export interface RailroadFeatureCollection {
  type: string;
  name: string;
  metadata: {
    version: number;
    generated_at: string;
    source: {
      path: string;
      feature_count: number;
      line_count: number;
    };
  };
  features: GeoJsonFeature[];
  crs?: unknown;
}
