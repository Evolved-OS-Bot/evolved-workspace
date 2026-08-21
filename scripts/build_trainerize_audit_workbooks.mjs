import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "/Users/peterbrown/evolved-workspace";
const publicDir = `${root}/outputs/trainerize-longitudinal-audit-2026-07-21`;
const privateDir = `${root}/data/private/trainerize-longitudinal-audit/analysis`;
const publicTables = JSON.parse(await fs.readFile(`${publicDir}/audit_tables.json`, "utf8"));
const privateTables = JSON.parse(await fs.readFile(`${privateDir}/private_tables.json`, "utf8"));

const COLORS = {
  navy: "#15304A",
  teal: "#1E9E8F",
  pale: "#DCEFEA",
  paleBlue: "#EAF1F7",
  text: "#17212B",
  muted: "#5D6B78",
  grid: "#D9E1E8",
  warning: "#FFF2CC",
};

function matrixFromRows(rows) {
  if (!rows.length) return { headers: ["No records"], matrix: [["No records"]] };
  const headers = Object.keys(rows[0]);
  return {
    headers,
    matrix: rows.map((row) => headers.map((header) => row[header] ?? null)),
  };
}

function columnLetter(index) {
  let n = index + 1;
  let out = "";
  while (n > 0) {
    n -= 1;
    out = String.fromCharCode(65 + (n % 26)) + out;
    n = Math.floor(n / 26);
  }
  return out;
}

function applyNumberFormats(sheet, headers, startRow, rowCount) {
  headers.forEach((header, index) => {
    const letter = columnLetter(index);
    const range = sheet.getRange(`${letter}${startRow}:${letter}${startRow + rowCount - 1}`);
    const lower = header.toLowerCase();
    if (lower.includes("pct")) range.setNumberFormat("0.0");
    else if (lower.includes("ratio")) range.setNumberFormat("0.000");
    else if (lower.includes("kg")) range.setNumberFormat("0.0");
    else if (lower === "value" || lower.includes("count") || lower.endsWith("_n") || lower.includes("days") || lower.includes("workouts") || lower.includes("participants") || lower.includes("rows") || lower.includes("threshold") || lower.includes("stage_number")) range.setNumberFormat("#,##0");
  });
}

function addDataSheet(workbook, name, title, subtitle, rows, options = {}) {
  const sheet = workbook.worksheets.add(name);
  sheet.showGridLines = false;
  const { headers, matrix } = matrixFromRows(rows);
  const lastCol = columnLetter(headers.length - 1);
  sheet.getRange(`A1:${lastCol}1`).merge();
  sheet.getRange("A1").values = [[title]];
  sheet.getRange(`A2:${lastCol}2`).merge();
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange(`A1:${lastCol}1`).format = {
    fill: COLORS.navy,
    font: { bold: true, color: "#FFFFFF", size: 16 },
    rowHeight: 28,
    verticalAlignment: "center",
  };
  sheet.getRange(`A2:${lastCol}2`).format = {
    fill: COLORS.paleBlue,
    font: { color: COLORS.muted, italic: true, size: 10 },
    wrapText: true,
    rowHeight: 34,
  };
  sheet.getRange(`A4:${lastCol}4`).values = [headers];
  sheet.getRange(`A4:${lastCol}4`).format = {
    fill: COLORS.teal,
    font: { bold: true, color: "#FFFFFF", size: 10 },
    wrapText: true,
    rowHeight: 32,
    borders: { preset: "all", style: "thin", color: COLORS.grid },
  };
  if (rows.length) {
    sheet.getRange(`A5:${lastCol}${rows.length + 4}`).values = matrix;
    sheet.getRange(`A5:${lastCol}${rows.length + 4}`).format = {
      font: { color: COLORS.text, size: 9 },
      verticalAlignment: "top",
      wrapText: options.wrap ?? false,
      borders: { preset: "all", style: "thin", color: COLORS.grid },
    };
    applyNumberFormats(sheet, headers, 5, rows.length);
  }
  sheet.freezePanes.freezeRows(4);
  sheet.getRange(`A4:${lastCol}${Math.min(rows.length + 4, 250)}`).format.autofitColumns();
  headers.forEach((header, index) => {
    const width = options.widths?.[header] ?? (header.includes("issue") || header.includes("impact") || header.includes("treatment") || header.includes("reason") ? 32 : 16);
    sheet.getRange(`${columnLetter(index)}:${columnLetter(index)}`).format.columnWidth = Math.min(width, 42);
  });
  return sheet;
}

function addReadme(workbook, isPrivate = false) {
  const sheet = workbook.worksheets.add("README");
  sheet.showGridLines = false;
  sheet.getRange("A1:H1").merge();
  sheet.getRange("A1").values = [[isPrivate ? "Trainerize Longitudinal Strength Audit: Private Review" : "Trainerize Longitudinal Strength Audit"]];
  sheet.getRange("A1:H1").format = { fill: COLORS.navy, font: { bold: true, color: "#FFFFFF", size: 18 }, rowHeight: 32 };
  const rows = [
    ["Audit date", "22 July 2026: expanded former-member extraction"],
    ["Purpose", "Describe what happens to logged strength performance after approximately 6, 12 and 24 months."],
    ["Study type", "Retrospective observational audit of Trainerize training logs. This is not a controlled scientific study."],
    ["Women's analysis cohort", `${publicTables.summary.confirmed_female_analysis_accounts} accounts explicitly recorded as female. The other ${publicTables.summary.accounts_excluded_from_womens_analysis} profiles comprise 34 missing, 7 male and 3 other Trainerize values. The owner reports onboarding errors; outcomes remain restricted until profile verification.`],
    ["Time origin", "Each participant's first completed detailed workout."],
    ["Baseline", "Best valid result during days 0-60."],
    ["Follow-up windows", "6 months: days 120-240; 12 months: days 300-450; 24 months: days 600-900; beyond 24 months: day 901+."],
    ["Loaded-lift score", "Epley estimated 1RM from 1-12 rep sets: weight × (1 + reps/30). Raw recorded weight and reps are retained."],
    ["Farmer Walk", "Only rows explicitly targeting 60 seconds or one minute. Historical load may be total or per hand, so interpretation is provisional."],
    ["Relative standards", "Require a bodyweight observation within ±45 days. Missing nearby bodyweight remains unavailable."],
    ["Material improvement", ">=20% improvement and >=5kg increase in the comparable movement score."],
    ["Nexus squat aliases", "Nexus Point Squat, Barbell Front Squat and Barbell Back Squat are the same exercise under unintended Trainerize names. Their loads are combined into one canonical Nexus outcome."],
    ["Exercise progression", "Goblet-to-Nexus progression is measured as a chronological stage transition. Goblet and canonical Nexus loads are not compared directly."],
    ["Marketing evidence", `${publicTables.summary.tracked_completed_workouts.toLocaleString()} tracked workouts and ${publicTables.summary.exercise_result_rows.toLocaleString()} exercise-result rows are available for confirmed-female accounts. Marketing wording and caveats are provided in a dedicated sheet.`],
    ["Expanded extraction", "A second pass recovered 3,130 detailed workouts from 46 additional former members with at least 120 days of logged history. Every temporarily changed account was restored."],
    ["Remarkable result", "A screening flag only. Coach validation and explicit member consent are required before public use."],
    ["Privacy", isPrivate ? "Contains names, email addresses and Trainerize IDs. Keep only in the private Evolved workspace." : "De-identified participant codes only. Do not attempt re-identification."],
    ["Critical limitation", "Later-horizon samples are selected survivors who kept training and logging. Always quote the paired sample size."],
  ];
  sheet.getRange(`A3:B${rows.length + 2}`).values = rows;
  sheet.getRange(`A3:A${rows.length + 2}`).format = { fill: COLORS.pale, font: { bold: true, color: COLORS.navy }, wrapText: true, borders: { preset: "all", style: "thin", color: COLORS.grid } };
  sheet.getRange(`B3:B${rows.length + 2}`).format = { font: { color: COLORS.text }, wrapText: true, borders: { preset: "all", style: "thin", color: COLORS.grid } };
  sheet.getRange("A:A").format.columnWidth = 24;
  sheet.getRange("B:B").format.columnWidth = 78;
  sheet.getRange(`A3:B${rows.length + 2}`).format.autofitRows();
  sheet.freezePanes.freezeRows(1);
  return sheet;
}

function addSummary(workbook, tables) {
  const sheet = workbook.worksheets.add("Audit Summary");
  sheet.showGridLines = false;
  sheet.getRange("A1:J1").merge();
  sheet.getRange("A1").values = [["Longitudinal Strength Audit: Executive Summary"]];
  sheet.getRange("A1:J1").format = { fill: COLORS.navy, font: { bold: true, color: "#FFFFFF", size: 18 }, rowHeight: 32 };
  sheet.getRange("A3:B3").values = [["Coverage metric", "Value"]];
  sheet.getRange("A3:B3").format = { fill: COLORS.teal, font: { bold: true, color: "#FFFFFF" }, borders: { preset: "all", style: "thin", color: COLORS.grid } };
  const metrics = [
    ["All non-test accounts", tables.summary.non_test_accounts],
    ["Confirmed-female analysis accounts", tables.summary.confirmed_female_analysis_accounts],
    ["Accounts not recorded as female", tables.summary.accounts_excluded_from_womens_analysis],
    ["Female accounts with tracked workouts", tables.summary.accounts_with_completed_calendar_workouts],
    ["Female accounts with detailed workouts", tables.summary.accounts_with_detailed_workouts],
    ["Active accounts with detail", tables.summary.active_accounts_with_detail],
    ["Deactivated accounts with detail", tables.summary.deactivated_accounts_with_detail],
    ["Source-recorded female tracked workouts", tables.summary.tracked_completed_workouts],
    ["All-account tracked programmed workouts", tables.summary.all_account_tracked_workouts],
    ["Detailed workouts", tables.summary.detailed_workouts],
    ["Recorded exercise results", tables.summary.exercise_result_rows],
    ["Participants with bodyweight", tables.summary.bodyweight_participants],
    ["Paired movement-horizon observations", tables.summary.paired_outcome_rows],
    ["Temporary changes left unrestored", tables.summary.unrestored_temporary_changes],
  ];
  metrics.forEach((row, index) => {
    const excelRow = index + 4;
    sheet.getRange(`A${excelRow}`).values = [[row[0]]];
    sheet.getRange(`B${excelRow}`).values = [[row[1]]];
  });
  sheet.getRange(`A4:B${metrics.length + 3}`).format = { borders: { preset: "all", style: "thin", color: COLORS.grid } };
  sheet.getRange(`A4:A${metrics.length + 3}`).format.fill = COLORS.paleBlue;
  sheet.getRange(`A4:A${metrics.length + 3}`).format.font = { bold: true, color: COLORS.navy };
  sheet.getRange(`B4:B${metrics.length + 3}`).setNumberFormat("#,##0");

  sheet.getRange("D3:G3").merge();
  sheet.getRange("D3").values = [["Most defensible paired outcomes"]];
  sheet.getRange("D3:G3").format = { fill: COLORS.teal, font: { bold: true, color: "#FFFFFF" } };
  const selectedMovements = ["Bench Press", "Deadlift", "Romanian Deadlift", "Nexus Point Squat"];
  const outcome = (movement, horizon) => tables.movement_outcomes.find(
    (row) => row.movement === movement && row.horizon === horizon,
  ) ?? {};
  const defensible = [
    ["Movement", "6m n", "6m median %", "12m median %"],
    ...selectedMovements.map((movement) => [
      movement,
      outcome(movement, "6 months (120-240d)").paired_participants ?? null,
      outcome(movement, "6 months (120-240d)").median_change_pct ?? null,
      outcome(movement, "12 months (300-450d)").median_change_pct ?? null,
    ]),
  ];
  sheet.getRange("D4:G8").values = defensible;
  sheet.getRange("D4:G4").format = { fill: COLORS.pale, font: { bold: true, color: COLORS.navy }, borders: { preset: "all", style: "thin", color: COLORS.grid } };
  sheet.getRange("D5:G8").format = { borders: { preset: "all", style: "thin", color: COLORS.grid } };
  sheet.getRange("F5:G8").setNumberFormat("0.0");

  sheet.getRange("A18:J18").merge();
  sheet.getRange("A18").values = [["Interpretation"]];
  sheet.getRange("A18:J18").format = { fill: COLORS.navy, font: { bold: true, color: "#FFFFFF" } };
  const notes = [
    "The dataset is operationally valuable and clearly supports a longitudinal product hypothesis, but it is not yet suitable for causal or population-wide scientific claims.",
    `Women's outcome analysis is restricted to ${tables.summary.confirmed_female_analysis_accounts} accounts explicitly recorded as female. The other ${tables.summary.accounts_excluded_from_womens_analysis} profiles are 34 missing, 7 male and 3 other in Trainerize. The owner reports onboarding errors, but the audit does not infer or overwrite sex without profile verification.`,
    "Bench press and deadlift provide the strongest combination of paired sample size and plausible improvement. RDL and the combined canonical Nexus Squat show larger gains, but programming changes and early low baselines may inflate percentage change.",
    `Detailed former-member coverage increased from 71 to ${tables.summary.deactivated_accounts_with_detail} accounts after a targeted second pass. Coverage remains incomplete and must not be represented as all-member outcomes.`,
    "24-month and beyond estimates are sparse for most individual movements. Treat them as case-finding signals, not stable population estimates.",
    "Farmer Walk results are retained but should not support external claims until the historical load convention (total versus per hand) is confirmed.",
    `${tables.summary.confirmed_goblet_to_nexus_participants} women have a clean observed pathway beginning with Goblet Squat and later reaching Nexus Point Squat. In total, ${tables.summary.observed_goblet_then_nexus_sequence_participants} show the sequence somewhere in their history, but many have earlier higher-stage records.`,
  ];
  notes.forEach((note, index) => {
    const row = 19 + index;
    sheet.getRange(`A${row}:J${row}`).merge();
    sheet.getRange(`A${row}`).values = [[`• ${note}`]];
    sheet.getRange(`A${row}:J${row}`).format = { wrapText: true, fill: index % 2 ? "#FFFFFF" : COLORS.paleBlue, font: { color: COLORS.text }, rowHeight: 36 };
  });
  sheet.getRange("A27:H27").values = [["Movement", "6m", "12m", "24m", null, null, null, null]];
  const helper = selectedMovements.map((movement) => {
    const byHorizon = Object.fromEntries(tables.movement_outcomes.filter((r) => r.movement === movement).map((r) => [r.horizon, r.median_change_pct]));
    return [movement, byHorizon["6 months (120-240d)"] ?? null, byHorizon["12 months (300-450d)"] ?? null, byHorizon["24 months (600-900d)"] ?? null];
  });
  sheet.getRange("A27:D31").values = [["Movement", "6m", "12m", "24m"], ...helper];
  sheet.getRange("A27:D27").format = { fill: COLORS.pale, font: { bold: true, color: COLORS.navy } };
  sheet.getRange("B28:D31").setNumberFormat("0.0");
  const chart = sheet.charts.add("bar", sheet.getRange("A27:D31"));
  chart.setPosition("F27", "J42");
  chart.title = "Median change from baseline (%)";
  chart.hasLegend = true;
  chart.yAxis = { numberFormatCode: "0.0" };
  sheet.getRange("A:A").format.columnWidth = 40;
  sheet.getRange("B:B").format.columnWidth = 16;
  sheet.getRange("D:G").format.columnWidth = 18;
  sheet.freezePanes.freezeRows(1);
  return sheet;
}

function addMarketingSummary(workbook, tables) {
  const sheet = workbook.worksheets.add("Marketing Summary");
  sheet.showGridLines = false;
  sheet.getRange("A1:J1").merge();
  sheet.getRange("A1").values = [["Marketing Evidence: Defensible Scale and Outcomes"]];
  sheet.getRange("A1:J1").format = { fill: COLORS.navy, font: { bold: true, color: "#FFFFFF", size: 18 }, rowHeight: 32 };
  sheet.getRange("A3:C3").values = [["Evidence metric", "Value", "How to use it"]];
  sheet.getRange("A3:C3").format = { fill: COLORS.teal, font: { bold: true, color: "#FFFFFF" }, wrapText: true };
  const evidence = Object.fromEntries(tables.marketing_evidence.map((row) => [row.metric, row]));
  const kpis = [
    "Tracked completed workouts",
    "Women with at least one tracked workout",
    "Exercise-result records",
    "Women with material improvement in at least 3 canonical movements",
    "Women advancing at least 2 mapped relative-strength standards",
    "Women with clean observed Goblet-to-Nexus progression",
  ].map((metric) => [metric, evidence[metric]?.value ?? null, evidence[metric]?.claim_status ?? null]);
  sheet.getRange(`A4:C${kpis.length + 3}`).values = kpis;
  sheet.getRange(`A4:C${kpis.length + 3}`).format = { borders: { preset: "all", style: "thin", color: COLORS.grid }, wrapText: true };
  sheet.getRange(`A4:A${kpis.length + 3}`).format = { fill: COLORS.paleBlue, font: { bold: true, color: COLORS.navy }, borders: { preset: "all", style: "thin", color: COLORS.grid }, wrapText: true };
  sheet.getRange(`B4:B${kpis.length + 3}`).setNumberFormat("#,##0");

  sheet.getRange("E3:J3").merge();
  sheet.getRange("E3").values = [["Approved public wording"]];
  sheet.getRange("E3:J3").format = { fill: COLORS.teal, font: { bold: true, color: "#FFFFFF" } };
  const publicClaims = tables.marketing_evidence.filter((row) => row.claim_status.startsWith("Marketing-ready"));
  publicClaims.slice(0, 5).forEach((row, index) => {
    const excelRow = 4 + index;
    sheet.getRange(`E${excelRow}:J${excelRow}`).merge();
    sheet.getRange(`E${excelRow}`).values = [[`• ${row.recommended_wording}`]];
    sheet.getRange(`E${excelRow}:J${excelRow}`).format = { fill: index % 2 ? "#FFFFFF" : COLORS.paleBlue, wrapText: true, rowHeight: 38, font: { color: COLORS.text } };
  });

  sheet.getRange("A13:J13").merge();
  sheet.getRange("A13").values = [["Marketing guardrails"]];
  sheet.getRange("A13:J13").format = { fill: COLORS.navy, font: { bold: true, color: "#FFFFFF" } };
  const guardrails = [
    "Say tracked workouts, not sessions attended: the calendar records completed workout items, not every coached appointment.",
    "Say recorded exercise results, not sets: one result row is not guaranteed to equal one completed set.",
    "Do not publish remarkable-result, standards or squat-progression counts as transformations until coaches validate the underlying records and members consent.",
    "Always retain the accessible-history date range and confirmed-female cohort definition when quoting scale.",
  ];
  guardrails.forEach((note, index) => {
    const row = 14 + index;
    sheet.getRange(`A${row}:J${row}`).merge();
    sheet.getRange(`A${row}`).values = [[`• ${note}`]];
    sheet.getRange(`A${row}:J${row}`).format = { wrapText: true, fill: index % 2 ? "#FFFFFF" : COLORS.warning, rowHeight: 34, font: { color: COLORS.text } };
  });

  const milestones = tables.marketing_milestones;
  sheet.getRange("A20:C20").values = [["Completed-workout milestone", "Women reaching milestone", "% of women with workouts"]];
  sheet.getRange(`A21:C${milestones.length + 20}`).values = milestones.map((row) => [row.completed_workout_threshold, row.confirmed_female_participants, row.pct_of_confirmed_female_participants_with_workouts]);
  sheet.getRange("A20:C20").format = { fill: COLORS.pale, font: { bold: true, color: COLORS.navy }, wrapText: true };
  sheet.getRange(`A21:C${milestones.length + 20}`).format = { borders: { preset: "all", style: "thin", color: COLORS.grid } };
  sheet.getRange(`A21:B${milestones.length + 20}`).setNumberFormat("#,##0");
  sheet.getRange(`C21:C${milestones.length + 20}`).setNumberFormat("0.0");
  const chart = sheet.charts.add("bar", sheet.getRange(`A20:B${milestones.length + 20}`));
  chart.setPosition("E20", "J35");
  chart.title = "Women reaching completed-workout milestones";
  chart.hasLegend = false;
  chart.yAxis = { numberFormatCode: "#,##0" };
  sheet.getRange("A:A").format.columnWidth = 38;
  sheet.getRange("B:B").format.columnWidth = 17;
  sheet.getRange("C:C").format.columnWidth = 30;
  sheet.freezePanes.freezeRows(1);
  return sheet;
}

const publicWorkbook = Workbook.create();
addReadme(publicWorkbook, false);
addSummary(publicWorkbook, publicTables);
addMarketingSummary(publicWorkbook, publicTables);
addDataSheet(publicWorkbook, "Marketing Evidence", "Marketing Evidence Register", "Use the recommended wording and retain every caveat. Outcome-screening rows are not publishable transformations without validation and consent.", publicTables.marketing_evidence, { wrap: true, widths: { metric: 38, recommended_wording: 58, claim_status: 34, caveat: 58 } });
addDataSheet(publicWorkbook, "Workout Milestones", "Completed Workout Milestones", "Confirmed-female accounts only. Counts describe accessible Trainerize history and are not retention or health-outcome rates.", publicTables.marketing_milestones, { wrap: true, widths: { completed_workout_threshold: 28, confirmed_female_participants: 30, pct_of_confirmed_female_participants_with_workouts: 38, claim_status: 34 } });
addDataSheet(publicWorkbook, "Family Exposure", "Movement-Family Exposure", "Related exercises are grouped for exposure coverage. Only Bilateral Squat currently has an ordered stage analysis.", publicTables.movement_family_exposure, { wrap: true });
addDataSheet(publicWorkbook, "Family Map", "Movement-Family Mapping Register", "Every source exercise remains visible. The three confirmed Nexus aliases combine; other exercise variants remain separate unless explicitly mapped.", publicTables.movement_family_map, { wrap: true, widths: { source_exercise_name: 42, comparison_rule: 58, mapping_status: 30 } });
addDataSheet(publicWorkbook, "Squat Stage Outcomes", "Squat Stage Outcomes by Horizon", "Two stages only: Goblet Squat, then canonical Nexus Point Squat. Stage changes are not kilogram changes.", publicTables.squat_progression_outcomes, { wrap: true, widths: { horizon: 26, paired_participants: 20, advanced_stage_n: 22, advanced_stage_pct: 22, confirmed_goblet_to_nexus_n: 24, confirmed_goblet_to_nexus_pct: 24, same_highest_stage_n: 22, lower_stage_only_n: 22, median_stage_change: 20, interpretation: 46 } });
addDataSheet(publicWorkbook, "Squat Lifetime", "De-identified Lifetime Squat Progressions", "Chronological Goblet-to-Nexus evidence across accessible history. The three confirmed Nexus source names are one canonical exercise.", publicTables.squat_lifetime_progressions, { wrap: true });
addDataSheet(publicWorkbook, "Squat Horizon Detail", "De-identified Squat Stage Transitions by Horizon", "Strict baseline and horizon-window transitions. Lower-stage-only observations are not evidence of regression.", publicTables.squat_progressions, { wrap: true });
addDataSheet(publicWorkbook, "Coverage", "Confirmed-Female Cohort Coverage", "Every account explicitly recorded as female. Detailed coverage must be used to qualify all outcome claims.", publicTables.coverage);
addDataSheet(publicWorkbook, "Movement Outcomes", "Paired Movement Outcomes", "Canonical comparable movements. The three confirmed Nexus source names are combined; source names remain visible in trajectories.", publicTables.movement_outcomes);
addDataSheet(publicWorkbook, "Standards Transitions", "Relative Strength Standard Transitions", "Only rows with a nearby bodyweight observation and a mapped standard.", publicTables.standards_transitions);
addDataSheet(publicWorkbook, "Remarkable Candidates", "Remarkable Result Screening Candidates", "Screening flags only. Validate the exercise record and obtain explicit member consent before public use.", publicTables.remarkable_candidates, { wrap: true });
addDataSheet(publicWorkbook, "Data Quality", "Data Quality Register", "Known limitations, their impact, and the treatment applied in this audit.", publicTables.data_quality, { wrap: true, widths: { issue: 28, impact: 42, treatment: 48 } });
addDataSheet(publicWorkbook, "Exercise Dictionary", "Trainerize Exercise Dictionary", "Raw observed exercise names remain distinct here. Confirmed analytical aliases are documented in Family Map.", publicTables.exercise_dictionary);
addDataSheet(publicWorkbook, "Trajectories", "De-identified Participant Trajectories", "Participant-level best results by movement and horizon. De-identified codes only.", publicTables.trajectories);

const publicXlsx = await SpreadsheetFile.exportXlsx(publicWorkbook);
await publicXlsx.save(`${publicDir}/trainerize_longitudinal_strength_audit_deidentified.xlsx`);

const privateWorkbook = Workbook.create();
addReadme(privateWorkbook, true);
addDataSheet(privateWorkbook, "Identified Trajectories", "Private Identified Member Trajectories", "Contains names, email addresses and Trainerize IDs. Do not upload or share outside the private Evolved workspace.", privateTables.identified_trajectories);
addDataSheet(privateWorkbook, "Identified Squat Lifetime", "Private Lifetime Squat Progressions", "Contains identities. Use for coach validation of the Goblet-to-Nexus pathway and never upload publicly.", privateTables.identified_squat_lifetime_progressions, { wrap: true });
addDataSheet(privateWorkbook, "Identified Squat Horizons", "Private Squat Stage Transitions by Horizon", "Contains identities. Stage transitions are not cross-exercise load comparisons.", privateTables.identified_squat_progressions, { wrap: true });
addDataSheet(privateWorkbook, "Restoration Log", "Temporary Account State Restoration Log", "Every temporary reactivation, verification state and restoration timestamp recorded during the audit.", privateTables.account_state_changes, { wrap: true });
const privateXlsx = await SpreadsheetFile.exportXlsx(privateWorkbook);
await privateXlsx.save(`${privateDir}/trainerize_longitudinal_strength_audit_private.xlsx`);

const inspectPublic = await publicWorkbook.inspect({ kind: "sheet", include: "id,name", maxChars: 6000 });
const inspectMarketing = await publicWorkbook.inspect({ kind: "table", sheetId: "Marketing Summary", range: "A1:J26", include: "values,formulas", tableMaxRows: 26, tableMaxCols: 10, maxChars: 9000 });
const inspectSquat = await publicWorkbook.inspect({ kind: "table", sheetId: "Squat Stage Outcomes", range: "A1:J8", include: "values,formulas", tableMaxRows: 8, tableMaxCols: 10, maxChars: 6000 });
const formulaErrors = await publicWorkbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 200 }, maxChars: 6000 });
const privateFormulaErrors = await privateWorkbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 200 }, maxChars: 6000 });
console.log(JSON.stringify({ inspectPublic, inspectMarketing, inspectSquat, formulaErrors, privateFormulaErrors }, null, 2));

const renderTargets = [
  ["README", "A1:H20"],
  ["Audit Summary", "A1:J42"],
  ["Marketing Summary", "A1:J35"],
  ["Marketing Evidence", "A1:G19"],
  ["Workout Milestones", "A1:D11"],
  ["Family Exposure", "A1:H12"],
  ["Family Map", "A1:K18"],
  ["Squat Stage Outcomes", "A1:J9"],
  ["Squat Lifetime", "A1:O18"],
  ["Squat Horizon Detail", "A1:N18"],
  ["Coverage", "A1:L18"],
  ["Movement Outcomes", "A1:N20"],
  ["Standards Transitions", "A1:K18"],
  ["Remarkable Candidates", "A1:H18"],
  ["Data Quality", "A1:C16"],
  ["Exercise Dictionary", "A1:H18"],
  ["Trajectories", "A1:O18"],
];
await fs.mkdir(`${publicDir}/previews`, { recursive: true });
for (const [sheetName, range] of renderTargets) {
  const blob = await publicWorkbook.render({ sheetName, range, scale: 1.2, format: "png" });
  await fs.writeFile(`${publicDir}/previews/${sheetName.replaceAll(" ", "_")}.png`, new Uint8Array(await blob.arrayBuffer()));
}

await fs.mkdir(`${privateDir}/previews`, { recursive: true });
for (const [sheetName, range] of [
  ["README", "A1:H20"],
  ["Identified Trajectories", "A1:S4"],
  ["Identified Squat Lifetime", "A1:S4"],
  ["Identified Squat Horizons", "A1:R4"],
  ["Restoration Log", "A1:I4"],
]) {
  const blob = await privateWorkbook.render({ sheetName, range, scale: 1.2, format: "png" });
  await fs.writeFile(`${privateDir}/previews/${sheetName.replaceAll(" ", "_")}.png`, new Uint8Array(await blob.arrayBuffer()));
}
