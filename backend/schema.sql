CREATE TABLE scans (
  id varchar(36) PRIMARY KEY,
  filename varchar(255) NOT NULL,
  status varchar(32) NOT NULL DEFAULT 'completed',
  files_scanned integer NOT NULL DEFAULT 0,
  findings_count integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT NOW(),
  updated_at timestamptz NOT NULL DEFAULT NOW()
);
CREATE TABLE findings (
  id varchar(36) PRIMARY KEY,
  scan_id varchar(36) NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
  file_path text NOT NULL,
  line_number integer NOT NULL,
  rule_id varchar(60) NOT NULL,
  severity varchar(12) NOT NULL,
  message varchar(255) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT NOW(),
  updated_at timestamptz NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_findings_scan_id ON findings(scan_id);
