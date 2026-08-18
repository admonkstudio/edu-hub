export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export type Database = {
  graphql_public: {
    Tables: {
      [_ in never]: never;
    };
    Views: {
      [_ in never]: never;
    };
    Functions: {
      graphql: {
        Args: {
          extensions?: Json;
          operationName?: string;
          query?: string;
          variables?: Json;
        };
        Returns: Json;
      };
    };
    Enums: {
      [_ in never]: never;
    };
    CompositeTypes: {
      [_ in never]: never;
    };
  };
  public: {
    Tables: {
      accreditation_bodies: {
        Row: {
          code: string;
          id: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order: number;
          status: string;
        };
        Insert: {
          code: string;
          id?: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order?: number;
          status?: string;
        };
        Update: {
          code?: string;
          id?: string;
          label_ar?: string;
          label_en?: string;
          slug_ar?: string;
          slug_en?: string;
          sort_order?: number;
          status?: string;
        };
        Relationships: [];
      };
      assertion_conflict_members: {
        Row: {
          assertion_id: string;
          conflict_id: string;
        };
        Insert: {
          assertion_id: string;
          conflict_id: string;
        };
        Update: {
          assertion_id?: string;
          conflict_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'assertion_conflict_members_assertion_id_fkey';
            columns: ['assertion_id'];
            isOneToOne: false;
            referencedRelation: 'entity_assertions';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'assertion_conflict_members_conflict_id_fkey';
            columns: ['conflict_id'];
            isOneToOne: false;
            referencedRelation: 'assertion_conflicts';
            referencedColumns: ['id'];
          },
        ];
      };
      assertion_conflicts: {
        Row: {
          created_at: string;
          entity_id: string;
          entity_type: string;
          field_key: string;
          id: string;
          locale: string | null;
          resolution_reason: string | null;
          resolved_at: string | null;
          resolved_by: string | null;
          status: string;
        };
        Insert: {
          created_at?: string;
          entity_id: string;
          entity_type: string;
          field_key: string;
          id?: string;
          locale?: string | null;
          resolution_reason?: string | null;
          resolved_at?: string | null;
          resolved_by?: string | null;
          status?: string;
        };
        Update: {
          created_at?: string;
          entity_id?: string;
          entity_type?: string;
          field_key?: string;
          id?: string;
          locale?: string | null;
          resolution_reason?: string | null;
          resolved_at?: string | null;
          resolved_by?: string | null;
          status?: string;
        };
        Relationships: [];
      };
      campus_facilities: {
        Row: {
          campus_id: string;
          facility_id: string;
        };
        Insert: {
          campus_id: string;
          facility_id: string;
        };
        Update: {
          campus_id?: string;
          facility_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'campus_facilities_campus_id_fkey';
            columns: ['campus_id'];
            isOneToOne: false;
            referencedRelation: 'campuses';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'campus_facilities_facility_id_fkey';
            columns: ['facility_id'];
            isOneToOne: false;
            referencedRelation: 'facilities';
            referencedColumns: ['id'];
          },
        ];
      };
      campuses: {
        Row: {
          address_ar: string | null;
          address_en: string | null;
          coordinates: unknown;
          created_at: string;
          id: string;
          institution_id: string;
          is_main: boolean;
          location_id: string;
          name: string;
          postal_code: string | null;
          status: string;
          updated_at: string;
        };
        Insert: {
          address_ar?: string | null;
          address_en?: string | null;
          coordinates?: unknown;
          created_at?: string;
          id?: string;
          institution_id: string;
          is_main?: boolean;
          location_id: string;
          name: string;
          postal_code?: string | null;
          status?: string;
          updated_at?: string;
        };
        Update: {
          address_ar?: string | null;
          address_en?: string | null;
          coordinates?: unknown;
          created_at?: string;
          id?: string;
          institution_id?: string;
          is_main?: boolean;
          location_id?: string;
          name?: string;
          postal_code?: string | null;
          status?: string;
          updated_at?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'campuses_institution_id_fkey';
            columns: ['institution_id'];
            isOneToOne: false;
            referencedRelation: 'institutions';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'campuses_location_id_fkey';
            columns: ['location_id'];
            isOneToOne: false;
            referencedRelation: 'locations';
            referencedColumns: ['id'];
          },
        ];
      };
      certificates: {
        Row: {
          code: string;
          id: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order: number;
          status: string;
        };
        Insert: {
          code: string;
          id?: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order?: number;
          status?: string;
        };
        Update: {
          code?: string;
          id?: string;
          label_ar?: string;
          label_en?: string;
          slug_ar?: string;
          slug_en?: string;
          sort_order?: number;
          status?: string;
        };
        Relationships: [];
      };
      change_sets: {
        Row: {
          actor_id: string;
          created_at: string;
          id: string;
          reason: string;
          source_id: string | null;
        };
        Insert: {
          actor_id: string;
          created_at?: string;
          id?: string;
          reason: string;
          source_id?: string | null;
        };
        Update: {
          actor_id?: string;
          created_at?: string;
          id?: string;
          reason?: string;
          source_id?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: 'change_sets_source_fk';
            columns: ['source_id'];
            isOneToOne: false;
            referencedRelation: 'sources';
            referencedColumns: ['id'];
          },
        ];
      };
      completeness_requirements: {
        Row: {
          critical: boolean;
          field_key: string;
          id: string;
          institution_type_id: string | null;
          stage: string;
          status: string;
        };
        Insert: {
          critical?: boolean;
          field_key: string;
          id?: string;
          institution_type_id?: string | null;
          stage: string;
          status?: string;
        };
        Update: {
          critical?: boolean;
          field_key?: string;
          id?: string;
          institution_type_id?: string | null;
          stage?: string;
          status?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'completeness_requirements_institution_type_id_fkey';
            columns: ['institution_type_id'];
            isOneToOne: false;
            referencedRelation: 'institution_types';
            referencedColumns: ['id'];
          },
        ];
      };
      curricula: {
        Row: {
          code: string;
          id: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order: number;
          status: string;
        };
        Insert: {
          code: string;
          id?: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order?: number;
          status?: string;
        };
        Update: {
          code?: string;
          id?: string;
          label_ar?: string;
          label_en?: string;
          slug_ar?: string;
          slug_en?: string;
          sort_order?: number;
          status?: string;
        };
        Relationships: [];
      };
      education_levels: {
        Row: {
          code: string;
          id: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order: number;
          status: string;
        };
        Insert: {
          code: string;
          id?: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order?: number;
          status?: string;
        };
        Update: {
          code?: string;
          id?: string;
          label_ar?: string;
          label_en?: string;
          slug_ar?: string;
          slug_en?: string;
          sort_order?: number;
          status?: string;
        };
        Relationships: [];
      };
      education_models: {
        Row: {
          code: string;
          id: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order: number;
          status: string;
        };
        Insert: {
          code: string;
          id?: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order?: number;
          status?: string;
        };
        Update: {
          code?: string;
          id?: string;
          label_ar?: string;
          label_en?: string;
          slug_ar?: string;
          slug_en?: string;
          sort_order?: number;
          status?: string;
        };
        Relationships: [];
      };
      entity_assertions: {
        Row: {
          assertion_status: string;
          confidence: number;
          created_at: string;
          created_by: string;
          entity_id: string;
          entity_type: string;
          field_key: string;
          id: string;
          locale: string | null;
          observed_at: string;
          review_reason: string | null;
          reviewed_at: string | null;
          reviewed_by: string | null;
          source_id: string;
          source_snapshot_id: string | null;
          updated_at: string;
          valid_from: string | null;
          valid_to: string | null;
          value_jsonb: Json;
        };
        Insert: {
          assertion_status?: string;
          confidence?: number;
          created_at?: string;
          created_by: string;
          entity_id: string;
          entity_type: string;
          field_key: string;
          id?: string;
          locale?: string | null;
          observed_at: string;
          review_reason?: string | null;
          reviewed_at?: string | null;
          reviewed_by?: string | null;
          source_id: string;
          source_snapshot_id?: string | null;
          updated_at?: string;
          valid_from?: string | null;
          valid_to?: string | null;
          value_jsonb: Json;
        };
        Update: {
          assertion_status?: string;
          confidence?: number;
          created_at?: string;
          created_by?: string;
          entity_id?: string;
          entity_type?: string;
          field_key?: string;
          id?: string;
          locale?: string | null;
          observed_at?: string;
          review_reason?: string | null;
          reviewed_at?: string | null;
          reviewed_by?: string | null;
          source_id?: string;
          source_snapshot_id?: string | null;
          updated_at?: string;
          valid_from?: string | null;
          valid_to?: string | null;
          value_jsonb?: Json;
        };
        Relationships: [
          {
            foreignKeyName: 'entity_assertions_source_id_fkey';
            columns: ['source_id'];
            isOneToOne: false;
            referencedRelation: 'sources';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'entity_assertions_source_snapshot_id_fkey';
            columns: ['source_snapshot_id'];
            isOneToOne: false;
            referencedRelation: 'source_snapshots';
            referencedColumns: ['id'];
          },
        ];
      };
      entity_revisions: {
        Row: {
          change_set_id: string;
          created_at: string;
          entity_id: string;
          entity_type: string;
          field_key: string;
          id: number;
          new_value: Json | null;
          old_value: Json | null;
          operation: string;
        };
        Insert: {
          change_set_id: string;
          created_at?: string;
          entity_id: string;
          entity_type: string;
          field_key: string;
          id?: never;
          new_value?: Json | null;
          old_value?: Json | null;
          operation: string;
        };
        Update: {
          change_set_id?: string;
          created_at?: string;
          entity_id?: string;
          entity_type?: string;
          field_key?: string;
          id?: never;
          new_value?: Json | null;
          old_value?: Json | null;
          operation?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'entity_revisions_change_set_id_fkey';
            columns: ['change_set_id'];
            isOneToOne: false;
            referencedRelation: 'change_sets';
            referencedColumns: ['id'];
          },
        ];
      };
      facilities: {
        Row: {
          code: string;
          id: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order: number;
          status: string;
        };
        Insert: {
          code: string;
          id?: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order?: number;
          status?: string;
        };
        Update: {
          code?: string;
          id?: string;
          label_ar?: string;
          label_en?: string;
          slug_ar?: string;
          slug_en?: string;
          sort_order?: number;
          status?: string;
        };
        Relationships: [];
      };
      field_freshness: {
        Row: {
          assertion_id: string | null;
          entity_id: string;
          entity_type: string;
          field_key: string;
          last_verified_at: string | null;
          next_review_at: string | null;
          status: string;
          updated_at: string;
        };
        Insert: {
          assertion_id?: string | null;
          entity_id: string;
          entity_type: string;
          field_key: string;
          last_verified_at?: string | null;
          next_review_at?: string | null;
          status?: string;
          updated_at?: string;
        };
        Update: {
          assertion_id?: string | null;
          entity_id?: string;
          entity_type?: string;
          field_key?: string;
          last_verified_at?: string | null;
          next_review_at?: string | null;
          status?: string;
          updated_at?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'field_freshness_assertion_id_fkey';
            columns: ['assertion_id'];
            isOneToOne: false;
            referencedRelation: 'entity_assertions';
            referencedColumns: ['id'];
          },
        ];
      };
      freshness_policies: {
        Row: {
          due_soon_days: number;
          entity_type: string;
          field_key: string;
          id: string;
          notes: string | null;
          priority: string;
          review_interval_days: number;
          status: string;
        };
        Insert: {
          due_soon_days?: number;
          entity_type: string;
          field_key: string;
          id?: string;
          notes?: string | null;
          priority?: string;
          review_interval_days: number;
          status?: string;
        };
        Update: {
          due_soon_days?: number;
          entity_type?: string;
          field_key?: string;
          id?: string;
          notes?: string | null;
          priority?: string;
          review_interval_days?: number;
          status?: string;
        };
        Relationships: [];
      };
      institution_accreditations: {
        Row: {
          accreditation_body_id: string;
          institution_id: string;
          valid_from: string | null;
          valid_to: string | null;
        };
        Insert: {
          accreditation_body_id: string;
          institution_id: string;
          valid_from?: string | null;
          valid_to?: string | null;
        };
        Update: {
          accreditation_body_id?: string;
          institution_id?: string;
          valid_from?: string | null;
          valid_to?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: 'institution_accreditations_accreditation_body_id_fkey';
            columns: ['accreditation_body_id'];
            isOneToOne: false;
            referencedRelation: 'accreditation_bodies';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'institution_accreditations_institution_id_fkey';
            columns: ['institution_id'];
            isOneToOne: false;
            referencedRelation: 'institutions';
            referencedColumns: ['id'];
          },
        ];
      };
      institution_certificates: {
        Row: {
          certificate_id: string;
          institution_id: string;
        };
        Insert: {
          certificate_id: string;
          institution_id: string;
        };
        Update: {
          certificate_id?: string;
          institution_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'institution_certificates_certificate_id_fkey';
            columns: ['certificate_id'];
            isOneToOne: false;
            referencedRelation: 'certificates';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'institution_certificates_institution_id_fkey';
            columns: ['institution_id'];
            isOneToOne: false;
            referencedRelation: 'institutions';
            referencedColumns: ['id'];
          },
        ];
      };
      institution_curricula: {
        Row: {
          curriculum_id: string;
          institution_id: string;
          valid_from: string | null;
          valid_to: string | null;
        };
        Insert: {
          curriculum_id: string;
          institution_id: string;
          valid_from?: string | null;
          valid_to?: string | null;
        };
        Update: {
          curriculum_id?: string;
          institution_id?: string;
          valid_from?: string | null;
          valid_to?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: 'institution_curricula_curriculum_id_fkey';
            columns: ['curriculum_id'];
            isOneToOne: false;
            referencedRelation: 'curricula';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'institution_curricula_institution_id_fkey';
            columns: ['institution_id'];
            isOneToOne: false;
            referencedRelation: 'institutions';
            referencedColumns: ['id'];
          },
        ];
      };
      institution_education_levels: {
        Row: {
          education_level_id: string;
          institution_id: string;
          valid_from: string | null;
          valid_to: string | null;
        };
        Insert: {
          education_level_id: string;
          institution_id: string;
          valid_from?: string | null;
          valid_to?: string | null;
        };
        Update: {
          education_level_id?: string;
          institution_id?: string;
          valid_from?: string | null;
          valid_to?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: 'institution_education_levels_education_level_id_fkey';
            columns: ['education_level_id'];
            isOneToOne: false;
            referencedRelation: 'education_levels';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'institution_education_levels_institution_id_fkey';
            columns: ['institution_id'];
            isOneToOne: false;
            referencedRelation: 'institutions';
            referencedColumns: ['id'];
          },
        ];
      };
      institution_languages: {
        Row: {
          institution_id: string;
          language_id: string;
        };
        Insert: {
          institution_id: string;
          language_id: string;
        };
        Update: {
          institution_id?: string;
          language_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'institution_languages_institution_id_fkey';
            columns: ['institution_id'];
            isOneToOne: false;
            referencedRelation: 'institutions';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'institution_languages_language_id_fkey';
            columns: ['language_id'];
            isOneToOne: false;
            referencedRelation: 'languages';
            referencedColumns: ['id'];
          },
        ];
      };
      institution_localizations: {
        Row: {
          alternate_names: string[];
          created_at: string;
          description: string | null;
          institution_id: string;
          locale: string;
          name: string;
          seo_description: string | null;
          seo_title: string | null;
          short_name: string | null;
          slug: string;
          summary: string | null;
          updated_at: string;
        };
        Insert: {
          alternate_names?: string[];
          created_at?: string;
          description?: string | null;
          institution_id: string;
          locale: string;
          name: string;
          seo_description?: string | null;
          seo_title?: string | null;
          short_name?: string | null;
          slug: string;
          summary?: string | null;
          updated_at?: string;
        };
        Update: {
          alternate_names?: string[];
          created_at?: string;
          description?: string | null;
          institution_id?: string;
          locale?: string;
          name?: string;
          seo_description?: string | null;
          seo_title?: string | null;
          short_name?: string | null;
          slug?: string;
          summary?: string | null;
          updated_at?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'institution_localizations_institution_id_fkey';
            columns: ['institution_id'];
            isOneToOne: false;
            referencedRelation: 'institutions';
            referencedColumns: ['id'];
          },
        ];
      };
      institution_types: {
        Row: {
          code: string;
          id: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order: number;
          status: string;
        };
        Insert: {
          code: string;
          id?: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order?: number;
          status?: string;
        };
        Update: {
          code?: string;
          id?: string;
          label_ar?: string;
          label_en?: string;
          slug_ar?: string;
          slug_en?: string;
          sort_order?: number;
          status?: string;
        };
        Relationships: [];
      };
      institutions: {
        Row: {
          claim_status: string;
          commercial_status: string;
          created_at: string;
          data_status: string;
          education_model_id: string | null;
          founded_year: number | null;
          id: string;
          institution_type_id: string;
          merged_into_id: string | null;
          official_name: string;
          official_website_url: string | null;
          ownership_type_id: string | null;
          provider_id: string | null;
          publication_status: string;
          updated_at: string;
        };
        Insert: {
          claim_status?: string;
          commercial_status?: string;
          created_at?: string;
          data_status?: string;
          education_model_id?: string | null;
          founded_year?: number | null;
          id?: string;
          institution_type_id: string;
          merged_into_id?: string | null;
          official_name: string;
          official_website_url?: string | null;
          ownership_type_id?: string | null;
          provider_id?: string | null;
          publication_status?: string;
          updated_at?: string;
        };
        Update: {
          claim_status?: string;
          commercial_status?: string;
          created_at?: string;
          data_status?: string;
          education_model_id?: string | null;
          founded_year?: number | null;
          id?: string;
          institution_type_id?: string;
          merged_into_id?: string | null;
          official_name?: string;
          official_website_url?: string | null;
          ownership_type_id?: string | null;
          provider_id?: string | null;
          publication_status?: string;
          updated_at?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'institutions_education_model_id_fkey';
            columns: ['education_model_id'];
            isOneToOne: false;
            referencedRelation: 'education_models';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'institutions_institution_type_id_fkey';
            columns: ['institution_type_id'];
            isOneToOne: false;
            referencedRelation: 'institution_types';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'institutions_merged_into_id_fkey';
            columns: ['merged_into_id'];
            isOneToOne: false;
            referencedRelation: 'institutions';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'institutions_ownership_type_id_fkey';
            columns: ['ownership_type_id'];
            isOneToOne: false;
            referencedRelation: 'ownership_types';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'institutions_provider_id_fkey';
            columns: ['provider_id'];
            isOneToOne: false;
            referencedRelation: 'providers';
            referencedColumns: ['id'];
          },
        ];
      };
      languages: {
        Row: {
          code: string;
          id: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order: number;
          status: string;
        };
        Insert: {
          code: string;
          id?: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order?: number;
          status?: string;
        };
        Update: {
          code?: string;
          id?: string;
          label_ar?: string;
          label_en?: string;
          slug_ar?: string;
          slug_en?: string;
          sort_order?: number;
          status?: string;
        };
        Relationships: [];
      };
      locations: {
        Row: {
          coordinates: unknown;
          country_code: string;
          created_at: string;
          id: string;
          location_type: string;
          name_ar: string;
          name_en: string;
          official_code: string | null;
          parent_id: string | null;
          slug_ar: string;
          slug_en: string;
          status: string;
          updated_at: string;
        };
        Insert: {
          coordinates?: unknown;
          country_code: string;
          created_at?: string;
          id?: string;
          location_type: string;
          name_ar: string;
          name_en: string;
          official_code?: string | null;
          parent_id?: string | null;
          slug_ar: string;
          slug_en: string;
          status?: string;
          updated_at?: string;
        };
        Update: {
          coordinates?: unknown;
          country_code?: string;
          created_at?: string;
          id?: string;
          location_type?: string;
          name_ar?: string;
          name_en?: string;
          official_code?: string | null;
          parent_id?: string | null;
          slug_ar?: string;
          slug_en?: string;
          status?: string;
          updated_at?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'locations_parent_id_fkey';
            columns: ['parent_id'];
            isOneToOne: false;
            referencedRelation: 'locations';
            referencedColumns: ['id'];
          },
        ];
      };
      ownership_types: {
        Row: {
          code: string;
          id: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order: number;
          status: string;
        };
        Insert: {
          code: string;
          id?: string;
          label_ar: string;
          label_en: string;
          slug_ar: string;
          slug_en: string;
          sort_order?: number;
          status?: string;
        };
        Update: {
          code?: string;
          id?: string;
          label_ar?: string;
          label_en?: string;
          slug_ar?: string;
          slug_en?: string;
          sort_order?: number;
          status?: string;
        };
        Relationships: [];
      };
      provider_localizations: {
        Row: {
          created_at: string;
          description: string | null;
          locale: string;
          name: string;
          provider_id: string;
          slug: string;
          updated_at: string;
        };
        Insert: {
          created_at?: string;
          description?: string | null;
          locale: string;
          name: string;
          provider_id: string;
          slug: string;
          updated_at?: string;
        };
        Update: {
          created_at?: string;
          description?: string | null;
          locale?: string;
          name?: string;
          provider_id?: string;
          slug?: string;
          updated_at?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'provider_localizations_provider_id_fkey';
            columns: ['provider_id'];
            isOneToOne: false;
            referencedRelation: 'providers';
            referencedColumns: ['id'];
          },
        ];
      };
      providers: {
        Row: {
          created_at: string;
          id: string;
          official_name: string;
          provider_type: string;
          status: string;
          updated_at: string;
          website_url: string | null;
        };
        Insert: {
          created_at?: string;
          id?: string;
          official_name: string;
          provider_type?: string;
          status?: string;
          updated_at?: string;
          website_url?: string | null;
        };
        Update: {
          created_at?: string;
          id?: string;
          official_name?: string;
          provider_type?: string;
          status?: string;
          updated_at?: string;
          website_url?: string | null;
        };
        Relationships: [];
      };
      research_tasks: {
        Row: {
          assertion_id: string | null;
          assigned_to: string | null;
          completed_at: string | null;
          completed_by: string | null;
          conflict_id: string | null;
          created_at: string;
          created_by: string;
          due_at: string | null;
          entity_id: string;
          entity_type: string;
          id: string;
          notes: string | null;
          outcome: string | null;
          priority: string;
          source_id: string | null;
          status: string;
          task_type: string;
          updated_at: string;
        };
        Insert: {
          assertion_id?: string | null;
          assigned_to?: string | null;
          completed_at?: string | null;
          completed_by?: string | null;
          conflict_id?: string | null;
          created_at?: string;
          created_by: string;
          due_at?: string | null;
          entity_id: string;
          entity_type?: string;
          id?: string;
          notes?: string | null;
          outcome?: string | null;
          priority?: string;
          source_id?: string | null;
          status?: string;
          task_type: string;
          updated_at?: string;
        };
        Update: {
          assertion_id?: string | null;
          assigned_to?: string | null;
          completed_at?: string | null;
          completed_by?: string | null;
          conflict_id?: string | null;
          created_at?: string;
          created_by?: string;
          due_at?: string | null;
          entity_id?: string;
          entity_type?: string;
          id?: string;
          notes?: string | null;
          outcome?: string | null;
          priority?: string;
          source_id?: string | null;
          status?: string;
          task_type?: string;
          updated_at?: string;
        };
        Relationships: [
          {
            foreignKeyName: 'research_tasks_assertion_id_fkey';
            columns: ['assertion_id'];
            isOneToOne: false;
            referencedRelation: 'entity_assertions';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'research_tasks_conflict_id_fkey';
            columns: ['conflict_id'];
            isOneToOne: false;
            referencedRelation: 'assertion_conflicts';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'research_tasks_entity_id_fkey';
            columns: ['entity_id'];
            isOneToOne: false;
            referencedRelation: 'institutions';
            referencedColumns: ['id'];
          },
          {
            foreignKeyName: 'research_tasks_source_id_fkey';
            columns: ['source_id'];
            isOneToOne: false;
            referencedRelation: 'sources';
            referencedColumns: ['id'];
          },
        ];
      };
      source_snapshots: {
        Row: {
          capture_method: string;
          content_hash: string;
          created_at: string;
          created_by: string;
          extracted_metadata: Json;
          id: string;
          retrieved_at: string;
          source_id: string;
          status: string;
          storage_path: string | null;
        };
        Insert: {
          capture_method?: string;
          content_hash: string;
          created_at?: string;
          created_by: string;
          extracted_metadata?: Json;
          id?: string;
          retrieved_at: string;
          source_id: string;
          status?: string;
          storage_path?: string | null;
        };
        Update: {
          capture_method?: string;
          content_hash?: string;
          created_at?: string;
          created_by?: string;
          extracted_metadata?: Json;
          id?: string;
          retrieved_at?: string;
          source_id?: string;
          status?: string;
          storage_path?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: 'source_snapshots_source_id_fkey';
            columns: ['source_id'];
            isOneToOne: false;
            referencedRelation: 'sources';
            referencedColumns: ['id'];
          },
        ];
      };
      sources: {
        Row: {
          authority_level: number;
          created_at: string;
          created_by: string;
          id: string;
          language: string;
          notes: string | null;
          published_at: string | null;
          publisher: string;
          retrieved_at: string;
          source_type: string;
          status: string;
          title: string;
          updated_at: string;
          url: string;
        };
        Insert: {
          authority_level: number;
          created_at?: string;
          created_by: string;
          id?: string;
          language: string;
          notes?: string | null;
          published_at?: string | null;
          publisher: string;
          retrieved_at?: string;
          source_type: string;
          status?: string;
          title: string;
          updated_at?: string;
          url: string;
        };
        Update: {
          authority_level?: number;
          created_at?: string;
          created_by?: string;
          id?: string;
          language?: string;
          notes?: string | null;
          published_at?: string | null;
          publisher?: string;
          retrieved_at?: string;
          source_type?: string;
          status?: string;
          title?: string;
          updated_at?: string;
          url?: string;
        };
        Relationships: [];
      };
      staff_users: {
        Row: {
          created_at: string;
          display_name: string | null;
          role: string;
          status: string;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          created_at?: string;
          display_name?: string | null;
          role: string;
          status?: string;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          created_at?: string;
          display_name?: string | null;
          role?: string;
          status?: string;
          updated_at?: string;
          user_id?: string;
        };
        Relationships: [];
      };
    };
    Views: {
      [_ in never]: never;
    };
    Functions: {
      create_institution_command: {
        Args: { payload: Json; reason: string };
        Returns: string;
      };
      institution_readiness: {
        Args: { institution_id: string };
        Returns: Json;
      };
      resolve_assertion_conflict_command: {
        Args: {
          accepted_assertion_id: string;
          conflict_id: string;
          reason: string;
        };
        Returns: undefined;
      };
      review_assertion_command: {
        Args: { assertion_id: string; decision: string; reason: string };
        Returns: undefined;
      };
      transition_research_task_command: {
        Args: {
          assigned_to: string;
          outcome?: string;
          status: string;
          task_id: string;
        };
        Returns: undefined;
      };
      update_institution_command: {
        Args: { institution_id: string; payload: Json; reason: string };
        Returns: string;
      };
    };
    Enums: {
      [_ in never]: never;
    };
    CompositeTypes: {
      [_ in never]: never;
    };
  };
};

type DatabaseWithoutInternals = Omit<Database, '__InternalSupabase'>;

type DefaultSchema = DatabaseWithoutInternals[Extract<
  keyof Database,
  'public'
>];

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema['Tables'] & DefaultSchema['Views'])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals;
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions['schema']]['Tables'] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions['schema']]['Views'])
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals;
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions['schema']]['Tables'] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions['schema']]['Views'])[TableName] extends {
      Row: infer R;
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema['Tables'] &
        DefaultSchema['Views'])
    ? (DefaultSchema['Tables'] &
        DefaultSchema['Views'])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R;
      }
      ? R
      : never
    : never;

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    keyof DefaultSchema['Tables'] | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals;
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions['schema']]['Tables']
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals;
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions['schema']]['Tables'][TableName] extends {
      Insert: infer I;
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema['Tables']
    ? DefaultSchema['Tables'][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I;
      }
      ? I
      : never
    : never;

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    keyof DefaultSchema['Tables'] | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals;
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions['schema']]['Tables']
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals;
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions['schema']]['Tables'][TableName] extends {
      Update: infer U;
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema['Tables']
    ? DefaultSchema['Tables'][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U;
      }
      ? U
      : never
    : never;

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    keyof DefaultSchema['Enums'] | { schema: keyof DatabaseWithoutInternals },
  EnumName extends (DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals;
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions['schema']]['Enums']
    : never) = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals;
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions['schema']]['Enums'][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema['Enums']
    ? DefaultSchema['Enums'][DefaultSchemaEnumNameOrOptions]
    : never;

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema['CompositeTypes']
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends (PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals;
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions['schema']]['CompositeTypes']
    : never) = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals;
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions['schema']]['CompositeTypes'][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema['CompositeTypes']
    ? DefaultSchema['CompositeTypes'][PublicCompositeTypeNameOrOptions]
    : never;

export const Constants = {
  graphql_public: {
    Enums: {},
  },
  public: {
    Enums: {},
  },
} as const;
