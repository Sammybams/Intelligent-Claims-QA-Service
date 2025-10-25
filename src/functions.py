claims_qa_response = {
  "format": {
    "type": "json_schema",
    "name": "simple_answer",
    "strict": True,
    "schema": {
      "title": "simple_answer",
      "description": "A simple response with a single string answer.",
      "type": "object",
      "properties": {
        "answer": { "type": "string" }
      },
      "required": ["answer"],
      "additionalProperties": False
    }
  }
}

extract_function = {
  "format": {
    "type": "json_schema",
    "name": "claims_summary_create",
    "strict": True,
    "schema": {
      "title": "claims_summary.create",
      "description": "Return a precise clinical/financial summary JSON for the provided document.",
      "type": "object",
      "properties": {
        "claims_id": { "type": "string" },

        "patient": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "id": { "type": "string" },
            "gender": { "type": "string" },
            "age": { "type": "integer" },
            "date_of_birth": { "type": "string", "format": "date" }
          },
          "required": ["name", "id", "gender", "age", "date_of_birth"],
          "additionalProperties": False
        },

        "demographics": {
          "type": "object",
          "properties": {
            "address": { "type": "string" },
            "phone": { "type": "string" }
          },
          "required": ["address", "phone"],
          "additionalProperties": False
        },

        "diagnoses": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
            },
            "required": ["name"],
            "additionalProperties": False
          }
        },

        "medications": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "dosage": { "type": "string" },
              "form": { "type": "string" },
              "frequency": { "type": "string" },
              "quantity": { "type": "string" },
              "unit_price": { "type": "number" },
              "total_price": { "type": "number" },
              "source": { "type": "string" },
              "raw_text_excerpt": { "type": "string" }
            },
            "required": ["name", "dosage", "form", "frequency", "quantity", "unit_price", "total_price", "source", "raw_text_excerpt"],
            "additionalProperties": False
          }
        },

        "procedures": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "quantity": { "type": "string" },
              "unit_price": { "type": "number" },
              "total_price": { "type": "number" },
            },
            "required": ["name", "quantity", "unit_price", "total_price"],
            "additionalProperties": False
          }
        },

        "admission": {
          "type": "object",
          "properties": {
            "was_admitted": { "type": "boolean" },
            "admission_date": { "type": "string", "format": "date" },
            "discharge_date": { "type": "string", "format": "date" },
            "ward": { "type": "string" },
            "bed_no": { "type": "string" }
          },
          "required": ["was_admitted", "admission_date", "discharge_date", "ward", "bed_no"],
          "additionalProperties": False
        },

        "vitals": {
          "type": "object",
          "properties": {},
          "required": [],
          "additionalProperties": False
        },

        "labs": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "test_name": { "type": "string" },
              "result": { "type": "string" },
              "units": { "type": "string" },
            },
            "required": ["test_name", "result", "units"],
            "additionalProperties": False
          }
        },

        "billing": {
          "type": "object",
          "properties": {
            "total_amount_str": { "type": "string" },
            "total_amount_value": { "type": "number" },
            "currency": { "type": "string" },
            "breakdown_table_id": { "type": "string" }
          },
          "required": ["total_amount_str", "total_amount_value", "currency", "breakdown_table_id"],
          "additionalProperties": False
        },

        "tables": {
          "type": "object",
          "properties": {},  
          "required": [], 
          "additionalProperties": {
            "type": "object",
            "properties": {
              "table_id": { "type": "string" },
              "columns": {
                "type": "array",
                "items": { "type": "string" }
              },
              "rows": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "row_id": { "type": "string" },
                    "cells": {
                      "type": "object",
                      "properties": {}, 
                      "additionalProperties": { "type": "string" },
                      "required": [] 
                    },
                  },
                  "required": ["row_id", "cells"],
                  "additionalProperties": False
                }
              }
            },
            "required": ["table_id", "columns", "rows"],
            "additionalProperties": False
          }
        },

        "notes": { "type": "string" },

        "metadata": {
          "type": "object",
          "properties": {},
          "required": [],
          "additionalProperties": False
        },

        "warnings": {
          "type": "array",
          "items": { "type": "string" }
        }
      },
      "required": [
        "claims_id",
        "patient",
        "demographics",
        "diagnoses",
        "medications",
        "procedures",
        "admission",
        "vitals",
        "labs",
        "billing",
        "tables",
        "notes",
        "metadata",
        "warnings"
      ],
      "additionalProperties": False
    }
  }
}