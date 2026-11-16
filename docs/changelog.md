# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

Each revision is versioned by the date of the revision.

## 2026-10-01

- Migrated the `terraform/charm` and `terraform/product` modules to the CC008
  Charm Terraform Standards: split the combined `provides` output into
  `kind`/`name`/`endpoint` objects, replaced the `app_name` output with an
  `application` object (charm module) and with `models`/`metadata`/`offers`
  outputs (product module), and renamed `versions.tf` to `terraform.tf`.
  Breaking default changes: the charm module's `base` and `constraints`
  variables now default to `null` instead of `"ubuntu@22.04"` and `""`.

## 2025-12-17

- Moved charm-architecture.md from Explanation to Reference category.

## 2025-12-04

- Added upgrade documentation.
