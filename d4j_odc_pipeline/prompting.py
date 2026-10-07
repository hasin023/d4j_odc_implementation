from __future__ import annotations

import json
import re

from .models import BugContext
from .odc import (
    STRATEGY_FEW,
    STRATEGY_ZERO,
    TAXONOMY_CLOSED,
    TAXONOMY_FREE,
    TAXONOMY_OPEN,
    allowed_type_names,
    taxonomy_markdown,
    validate_condition,
)

# Version of the few/scientific prompt text, written into every classification
# artifact (ClassificationResult.prompt_version). Bump it whenever the shared
# guidance, the taxonomy rendering or the worked examples change, and log the
# change in docs/study_execution_log.md. "v3-2026-10-05": real worked examples,
# IBM-only taxonomy, pre-July guidance removed — rationale in
# docs/prompt_review_v3.md. "v3.1-2026-10-07": the scientific loop's gate
# rules (numbered observations, evidence_from backtracking, outline quotes);
# the few/zero prompt text is byte-identical to v3. Artifacts without the
# field predate it.
PROMPT_VERSION = "v3.1-2026-10-07"


def build_messages(
    context: BugContext,
    taxonomy: str,
    strategy: str,
) -> list[dict[str, str]]:
    """Build the single-call LLM messages for one classification condition.

    Only the STATIC strategies are built here:
    - zero (taxonomy-free, no examples — the unstructured baseline)
    - few  (taxonomy + diagnostic tree + worked examples — the strong static prompt)
    The 'scientific' strategy (the enforced loop) builds its own conversation
    in agent.py and never calls this. See docs/condition_model.md.
    """
    validate_condition(taxonomy, strategy)
    if strategy not in (STRATEGY_ZERO, STRATEGY_FEW):
        raise ValueError(
            f"build_messages only handles static strategies (zero|few); got {strategy!r} — "
            "the scientific strategy is driven by agent.run_agentic_classification."
        )
    has_fix_diff = bool(context.fix_diff)
    system_prompt = _build_system_prompt(
        taxonomy=taxonomy, strategy=strategy, has_fix_diff=has_fix_diff
    )
    user_prompt = _build_user_prompt(context, taxonomy=taxonomy, strategy=strategy)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _build_system_prompt(
    *,
    taxonomy: str,
    strategy: str,
    has_fix_diff: bool = False,
) -> str:
    # zero: no ODC types, no structured labels, no anti-bias rules.
    # The LLM answers in its own words (simplified JSON contract).
    if strategy == STRATEGY_ZERO:
        return _build_zero_system_prompt(has_fix_diff=has_fix_diff)
    taxonomy_mode = taxonomy

    base = [
        "You are an expert software defect analyst specializing in Orthogonal Defect Classification (ODC).",
    ]

    base.extend(_evidence_mode_guidance(has_fix_diff))
    base.extend([
        *_critical_rules(),
        "",
        taxonomy_markdown(taxonomy_mode),
        "",
        "Return only valid JSON matching this schema:",
        _json_contract(taxonomy_mode),
    ])
    # Worked examples — the "shots" that make this the few-shot strategy. Kept
    # last (nearest the input): the order decision rests on recency bias, see
    # docs/few_shot_worked_examples_research.md Q6.1 decision 6.
    base.extend(["", _few_shot_examples()])
    return "\n".join(base)


# The ODC guidance blocks below are shared verbatim by `few` (this module) and
# `scientific` (agent.py), so the two strategies differ ONLY by the loop.


# IBM ODC v5.2 §4.2: "Defect Type: Represents the actual correction that was made."
_IBM_CORRECTION_RULE = 'In ODC, a defect type describes "the actual correction that was made" (IBM ODC v5.2)'


def _evidence_mode_guidance(has_fix_diff: bool) -> list[str]:
    """The task statement for the evidence mode, shared by `few` and `scientific`.

    Pre-fix: classify from pre-fix evidence, judging the correction the bug needs.
    Post-fix: the diff shows the correction, so classify its nature.
    """
    if has_fix_diff:
        return _fix_diff_guidance()
    return [
        "Your job is to classify one bug into exactly one type from the taxonomy below, using ONLY the provided pre-fix evidence.",
        f"{_IBM_CORRECTION_RULE}, so judge what kind of correction the evidence shows the bug needs.",
    ]


def _fix_diff_guidance() -> list[str]:
    # The seven "If the diff ... -> type" lines that used to follow were removed
    # 2026-10-05 (docs/prompt_review_v3.md, block 2): one contradicted IBM's
    # Algorithm illustration (3) and worked example 5, and as surface rules they
    # match the post-fix failure in the manual analysis (finding 7).
    return [
        "You are classifying a bug using BOTH pre-fix evidence AND the actual buggy-to-fixed diff.",
        "The diff shows exactly what was changed to fix the bug.",
        f"{_IBM_CORRECTION_RULE}, so classify the nature of this change.",
        "",
        "IMPORTANT: The diff is the GROUND TRUTH of what was fixed. Your classification should be",
        "consistent with the nature of the change shown in the diff.",
    ]


def _critical_rules() -> list[str]:
    # Reduced 2026-10-05 (docs/prompt_review_v3.md, block 3): the "Do NOT default
    # to Function/Class/Object" rule is now covered by IBM's FCO definition and
    # worked example 5; "the type of fix needed determines the ODC type" moved
    # into _evidence_mode_guidance in IBM's words. The classification decision
    # process (7 ranked diagnostic questions) was removed too (block 6).
    return [
        "",
        "CRITICAL RULES:",
        "- Do not use benchmark familiarity, project reputation, or hidden fix knowledge.",
    ]


# The 7 worked examples: real bugs from the Coimbra NoSQL ODC dataset (Agnelo,
# Laranjeiro, Bernardino, JSS 159, 2020), one per ODC type, in the decided order
# (Checking ... Timing/Serialization; recency bias, Zhao et al. 2021). Report and
# code lines are copied word for word from the public JIRA issues and fix commits;
# [...] marks every cut; the `//` file labels are ours. The same set goes into both
# evidence modes. Approved one by one by the user on 2026-10-04/05: text,
# provenance and rationale in docs/worked_examples_draft.md. No worked example for
# "Other", by decision (docs/other_category.md §4). No other block may refer to
# this one, so an IBM-taxonomy-only variant can leave it out.
_WORKED_EXAMPLES_INTRO = (
    "The short examples inside each definition above are IBM's. The worked examples below are real bugs "
    "from other projects (Apache Cassandra and HBase), each labeled by ODC researchers, with the evidence, "
    "the real fix, the type the fix points to, and, for most, why a close type does not fit. They show how "
    "to reason; they are not related to the bug you are classifying."
)

# Each item is wrapped in newlines so it may end with a quote mark; strip them.
_WORKED_EXAMPLES: tuple[str, ...] = tuple(example.strip("\n") for example in (
    r"""
### Worked example 1: Checking
**Bug report**: "Deprecated repair methods cause NPE" — "The deprecated repair methods cause an NPE if you aren't doing local repairs."
**Buggy code**:
```java
// StorageService.java, deprecated forceRepairRangeAsync(..., boolean isLocal, ...)
Set<String> dataCenters = null;
if (isLocal)
{
    dataCenters = Sets.newHashSet(DatabaseDescriptor.getLocalDataCenter());
}
return forceRepairRangeAsync(beginToken, endToken, keyspaceName, isSequential, dataCenters, null, fullRepair, tableNames);
[…]
// StorageService.java, the forceRepairRangeAsync(...) it calls
options.getDataCenters().addAll(dataCenters);
if (hosts != null)
{
    options.getHosts().addAll(hosts);
```
**Fix**:
```diff
-        options.getDataCenters().addAll(dataCenters);
+        if (dataCenters != null)
+        {
+            options.getDataCenters().addAll(dataCenters);
+        }
```
**Type**: **Checking** — "missing or incorrect validation of parameters or data in conditional statements". The fix adds the missing null check; nothing else changes.
**Why not Algorithm/Method**: the fix adds a branch, but it only wraps an existing statement in a null check; no computation is implemented or changed. IBM: "It might be expected that a consequence of checking for a value would require additional code such as a do while loop or branch. If the missing or incorrect check is the critical error, checking would still be the type chosen."
""",
    r"""
### Worked example 2: Assignment/Initialization
**Bug report**: "Set default value for hbase.client.scanner.max.result.size" — "Setting scanner caching is somewhat of a black art. It's hard to estimate ahead of time how large the result set will be. I propose we hbase.client.scanner.max.result.size to 2mb. That is good compromise between performance and buffer usage on typical networks (avoiding OOMs when the caching was chosen too high)." A comment: "avoided full GCs due to many handlers allocating too many big chunks for responses".
**Buggy code**:
```java
// HConstants.java
   * The default value is unlimited.
   */
  public static final long DEFAULT_HBASE_CLIENT_SCANNER_MAX_RESULT_SIZE = Long.MAX_VALUE;
```
**Fix**:
```diff
-  public static final long DEFAULT_HBASE_CLIENT_SCANNER_MAX_RESULT_SIZE = Long.MAX_VALUE;
+  public static final long DEFAULT_HBASE_CLIENT_SCANNER_MAX_RESULT_SIZE = 2 * 1024 * 1024;
```
**Type**: **Assignment/Initialization** — "Value(s) assigned incorrectly"; IBM's illustration "Initialization of parameters". One constant gets a new value.
**Why not Algorithm/Method**: IBM: "a fix involving multiple assignment corrections may be of type Algorithm." Here the fix corrects a single value, and no other code changes.
""",
    r"""
### Worked example 3: Algorithm/Method
**Bug report**: "nodetool prints error if dirs don't exist." — "./nodetool ring […] ERROR 21:59:30 Fatal configuration error org.apache.cassandra.exceptions.ConfigurationException: commitlog_directory is missing and -Dcassandra.storagedir is not set at org.apache.cassandra.config.DatabaseDescriptor.applyConfig(DatabaseDescriptor.java:461) […] at org.apache.cassandra.config.DatabaseDescriptor.<clinit>(DatabaseDescriptor.java:129) […] at org.apache.cassandra.tools.NodeTool$Ring.execute(NodeTool.java:464)"
**Buggy code**:
```java
// NodeTool.java, Ring.execute()
for (Map.Entry<String, String> entry : tokensToEndpoints.entrySet())
    endpointsToTokens.put(entry.getValue(), entry.getKey());
[…]
if (DatabaseDescriptor.getNumTokens() > 1)
{
    System.out.println("  Warning: \"nodetool ring\" is used to output all the tokens of a node.");
```
**Fix**:
```diff
+            boolean haveVnodes = false;
             for (Map.Entry<String, String> entry : tokensToEndpoints.entrySet())
+            {
+                haveVnodes |= endpointsToTokens.containsKey(entry.getValue());
                 endpointsToTokens.put(entry.getValue(), entry.getKey());
+            }
[…]
-            if (DatabaseDescriptor.getNumTokens() > 1)
+            if (haveVnodes)
```
**Type**: **Algorithm/Method** — "can be fixed by (re)implementing an algorithm or local data structure without the need for requesting a design change". The way the tool decides "are vnodes in use?" was reimplemented: instead of reading the local configuration, it checks whether any node owns more than one token in the token map it already has.
**Why not Checking**: the fix edits an `if`, but that condition validates no parameter or data; it only decides whether to print a warning. What changed is how its value is computed.
**Why not Assignment/Initialization**: `haveVnodes` is a new variable, but no existing value was wrong; its value comes from a new loop over the token map.
**Why not Interface/O-O Messages**: the fix does not correct the call to `DatabaseDescriptor`; it removes the call and computes the answer with a new loop over the token map the tool already had.
""",
    r"""
### Worked example 4: Interface/O-O Messages
**Bug report**: "dtest failure upgrade_tests.upgrade_supercolumns_test.TestSCUpgrade.upgrade_super_columns_through_all_versions_test" — "The test complains about unreadable sstables version ka and lb during upgrade which is 2.1 and 2.2. These tables look like system tables not user tables. […] nodetool defaults to only upgrading user tables and doesn't have a flag to upgrade all tables."
**Buggy code**:
```java
// UpgradeSSTable.java, execute()
List<String> keyspaces = parseOptionalKeyspace(args, probe);
```
```java
// NodeTool.java
protected List<String> parseOptionalKeyspace(List<String> cmdArgs, NodeProbe nodeProbe)
{
    return parseOptionalKeyspace(cmdArgs, nodeProbe, false);
}

protected List<String> parseOptionalKeyspace(List<String> cmdArgs, NodeProbe nodeProbe, boolean includeSystemKS)
{
    […]
        keyspaces.addAll(includeSystemKS ? nodeProbe.getKeyspaces() : nodeProbe.getNonSystemKeyspaces());
```
**Fix**:
```diff
-        List<String> keyspaces = parseOptionalKeyspace(args, probe);
+        List<String> keyspaces = parseOptionalKeyspace(args, probe, true);
```
**Type**: **Interface/O-O Messages** — "Communication problems between […] functions via […] call statements, […] parameter lists". The capability already existed. The caller used the 2-parameter version, so the system keyspaces were never requested; the fix passes the third parameter.
**Why not Function/Class/Object**: the report asks for a flag, but nothing new was built; the 3-parameter version already existed. The fix changes only the call.
**Why not Assignment/Initialization**: no variable or field is given a new value. The fix changes the call's parameter list, from 2 arguments to 3.
""",
    r"""
### Worked example 5: Function/Class/Object
**Bug report**: "sstableloader does not support client encryption on Cassandra 2.0" — "When client_enc_enable: true, the exception below is generated. However, when client_enc_enable is set to false, the sstableloader is able to get to the point where it is discovers endpoints, connects to stream data, etc. […] Exception in thread "main" java.lang.RuntimeException: Could not retrieve endpoint ranges: at org.apache.cassandra.tools.BulkLoader$ExternalClient.init(BulkLoader.java:226) […] Caused by: org.apache.thrift.transport.TTransportException: Frame size (352518400) larger than max length (16384000)! at org.apache.thrift.transport.TFramedTransport.readFrame(TFramedTransport.java:137)"
**Buggy code**:
```java
// BulkLoader.java, ExternalClient.createThriftClient()
private static Cassandra.Client createThriftClient(String host, int port, String user, String passwd) throws Exception
{
    TSocket socket = new TSocket(host, port);
    TTransport trans = new TFramedTransport(socket);
    trans.open();
```
**Fix**:
```diff
// SSLTransportFactory.java (new file)
+public class SSLTransportFactory implements ITransportFactory
[…]
+    public TTransport openTransport(String host, int port) throws Exception
+    {
+        TSSLTransportFactory.TSSLTransportParameters params = new TSSLTransportFactory.TSSLTransportParameters(protocol, cipherSuites);
+        params.setTrustStore(truststore, truststorePassword);
[…]
```
```diff
// BulkLoader.java
-        private static Cassandra.Client createThriftClient(String host, int port, String user, String passwd) throws Exception
+        private static Cassandra.Client createThriftClient(String host, int port, String user, String passwd, ITransportFactory transportFactory) throws Exception
         {
-            TSocket socket = new TSocket(host, port);
-            TTransport trans = new TFramedTransport(socket);
-            trans.open();
+            TTransport trans = transportFactory.openTransport(host, port);
[…]
+            options.addOption("ts", SSL_TRUSTSTORE, "TRUSTSTORE", "SSL: full path to truststore");
+            options.addOption("tspw", SSL_TRUSTSTORE_PW, "TRUSTSTORE-PASSWORD", "SSL: password of the truststore");
+            options.addOption("ks", SSL_KEYSTORE, "KEYSTORE", "SSL: full path to keystore");
[…]
```
**Type**: **Function/Class/Object** — "The error should require a formal design change, as it affects significant capability, end-user interfaces, product interfaces, interface with hardware architecture, or global data structure(s)". The loader could open only a plain connection, so it could not work when client encryption was enabled. The fix adds that capability: a new class that opens encrypted connections, and new command-line options for users to configure it.
**Why not Algorithm/Method**: IBM's Algorithm fixes come "without the need for requesting a design change". This fix adds a new class and new options for users.
**Why not Interface/O-O Messages**: the fix adds a parameter to `createThriftClient`, but no existing call was wrong; the new parameter carries the new capability to where the connection is opened.
""",
    r"""
### Worked example 6: Relationship
**Bug report**: "FunctionExecutionException results in error log about unexpected error" — "Because FunctionExecutionException doesn't extend RequestExecutionException, a failure during the execution of a UDF will result in a error log in QueryMessage about "Unexpected error during query"."
**Buggy code**:
```java
// QueryMessage.java, execute()
catch (Exception e)
{
    JVMStabilityInspector.inspectThrowable(e);
    if (!((e instanceof RequestValidationException) || (e instanceof RequestExecutionException)))
        logger.error("Unexpected error during query", e);
```
```java
// FunctionExecutionException.java
public class FunctionExecutionException extends CassandraException
```
**Fix**:
```diff
-public class FunctionExecutionException extends CassandraException
+public class FunctionExecutionException extends RequestExecutionException
```
**Type**: **Relationship** — IBM's illustrations "The inheritance relationship between two classes is missing or incorrectly specified" and "The structure of code/data in one place assumes a certain structure of code/data in another." `QueryMessage` treats an error as expected only if it is a `RequestValidationException` or a `RequestExecutionException`; `FunctionExecutionException` had neither parent. The fix gives it the right parent class and leaves the `catch` block unchanged.
""",
    r"""
### Worked example 7: Timing/Serialization
**Bug report**: "concurrent modif ex when repair is run on LCS" — "[…] the problem is the sstable list in the manifest is changing as the repair is triggered:
Exception in thread "main" java.util.ConcurrentModificationException
 at java.util.AbstractList$Itr.checkForComodification(Unknown Source)
 at java.util.AbstractList$Itr.next(Unknown Source)
 at org.apache.cassandra.io.sstable.SSTable.getTotalBytes(SSTable.java:250)
 at org.apache.cassandra.db.compaction.LeveledManifest.getEstimatedTasks(LeveledManifest.java:435)
 at org.apache.cassandra.db.compaction.LeveledCompactionStrategy.getEstimatedRemainingTasks(LeveledCompactionStrategy.java:128)
[…]
maybe we could change the list to a copyOnArrayList?"
**Buggy code**:
```java
// LeveledManifest.java
public synchronized void add(SSTableReader reader)
[…]
public synchronized void promote(Iterable<SSTableReader> removed, Iterable<SSTableReader> added)
[…]
public synchronized void replace(Iterable<SSTableReader> removed, Iterable<SSTableReader> added)
[…]
public int getEstimatedTasks()
{
    long tasks = 0;
    for (int i = generations.length - 1; i >= 0; i--)
    {
        List<SSTableReader> sstables = generations[i];
        long n = Math.max(0L, SSTableReader.getTotalBytes(sstables) - maxBytesForLevel(i)) / (maxSSTableSizeInMB * 1024 * 1024);
```
**Fix**:
```diff
-    public int getEstimatedTasks()
+    public synchronized int getEstimatedTasks()
```
**Type**: **Timing/Serialization** — "Necessary serialization of shared resource was missing". The methods that change the level lists are `synchronized`; `getEstimatedTasks()` reads the same lists without the lock, so it can iterate a list while another thread changes it. The fix adds the missing lock.
**Why not Algorithm/Method**: the reporter suggested switching to a different list type (CopyOnWriteArrayList), and IBM's Algorithm covers "(re)implementing an algorithm or local data structure". But the actual correction keeps the list and the computation as they are, and only adds the lock the other methods already hold.
""",
))


def _few_shot_examples() -> str:
    lines = ["## Worked examples", "", _WORKED_EXAMPLES_INTRO, "", "<worked_examples>"]
    for example in _WORKED_EXAMPLES:
        lines.extend(["<example>", example, "</example>"])
    lines.append("</worked_examples>")
    return "\n".join(lines)


def _build_user_prompt(
    context: BugContext,
    *,
    taxonomy: str,
    strategy: str,
) -> str:
    payload = _context_payload(context)
    evidence_mode = "post-fix (with buggy->fixed diff)" if context.fix_diff else "pre-fix only"
    taxonomy_mode = taxonomy

    # zero-shot: no ODC references in user prompt either.
    if strategy == STRATEGY_ZERO:
        rules = [
            "Classify this bug based on the evidence below.",
            f"Evidence mode: {evidence_mode}",
            "",
            "ANALYSIS RULES:",
            "- Use ONLY the evidence provided.",
            "- Examine code snippets carefully to determine the root cause.",
            "- Focus on WHAT is wrong in the code, not just the symptom.",
            "- Be specific and technical in your defect type label.",
        ]
        if context.fix_diff:
            rules.append("- Examine the fix diff to see exactly what was changed.")
        return "\n".join(rules) + "\n\nEvidence:\n" + json.dumps(payload, indent=2)

    rules = [
        "Classify this bug into exactly one type from the taxonomy.",
        f"Evidence mode: {evidence_mode}",
        "",
        "IMPORTANT ANALYSIS RULES:",
        "- Use ONLY the evidence in this prompt.",
        "- Examine code snippets line-by-line to determine the root cause mechanism.",
        "- If evidence is incomplete, lower confidence and set needs_human_review=true.",
        "- The output odc_type must be one of: " + ", ".join(allowed_type_names(taxonomy_mode)),
    ]
    if taxonomy_mode == TAXONOMY_OPEN:
        rules.append(
            "- 'Other' is a LAST RESORT: only when the root-cause mechanism fits none of the 7 ODC "
            "types. Uncertainty or incomplete evidence is NOT a reason to choose Other. If you choose "
            "Other, you MUST fill other_justification, nearest_type, and other_confidence."
        )
    if context.fix_diff:
        rules.append("- CAREFULLY examine the fix_diff_oracle to see exactly what was changed. The nature of the change determines the ODC type.")
    return "\n".join(rules) + "\n\nEvidence:\n" + json.dumps(payload, indent=2)


# ── Pre-fix payload sanitization ──────────────────────────────────────────
# The pre-fix arm must contain NO fix-derived information (see
# docs/odc_alignment_audit.md §7). Two channels are sanitized at payload-build
# time — context.json artifacts are never modified:
#   - bug_info: raw `defects4j info` output carries "List of modified sources"
#     (the classes changed by the FIX commit — the same oracle hidden as
#     hidden_oracles["classes.modified"]) and the fixed-revision id/date.
#   - bug_report_content: tracker pages/API responses carry post-fix material
#     (comments like "Fixed in …", Status/Resolution fields, close transitions).
# Post-fix payloads (context.fix_diff set) keep both untouched: that arm
# legitimately knows the fix.

_BUG_INFO_FIX_SECTIONS = (
    "revision id (fixed version)",
    "revision date (fixed version)",
    "list of modified sources",
)

# Comment-thread markers for flattened tracker pages (SourceForge, archives).
# Truncating at the earliest marker keeps the original report body, which
# always precedes the comment thread.
# NOTE: "If you would like to refer to this comment" / "Logged In: YES" are
# boilerplate APPENDED AFTER each individual comment, not before the thread —
# truncating there still keeps the first comment's own text intact (which is
# exactly where a "Good spot, I've committed the fix" disclosure typically
# lives). "Discussion" is SourceForge's section header preceding the FIRST
# comment, so it must be tried first; the others remain as a fallback for
# pages where "Discussion" doesn't appear. Verified against the corpus:
# 23/832 reports contain "Discussion", 100% as this section-header pattern
# (never inside legitimate description prose).
_REPORT_COMMENT_MARKERS = (
    "\nComments:",                                  # our own JIRA/GitHub API format
    "Discussion",                                    # SourceForge section header (precedes ALL comments)
    "If you would like to refer to this comment",   # SourceForge per-comment boilerplate (fallback)
    "Logged In: YES",                               # SourceForge comment header (fallback)
    "Log in to post a comment",                     # SourceForge page footer (fallback)
)

# Google Code-style trackers (e.g. Closure) store the report as a raw JSON
# object: {"status": "...", "comments": [{"id":0,...="original report"},
# {"id":1,...="follow-up discussion, routinely reveals the fix"}, ...]}.
# The first comment IS the original report; truncate at the second comment
# object's start regardless of its "id" value (ids are not guaranteed to
# start at a specific number).
_JSON_SECOND_COMMENT_RE = re.compile(r'\{"id":\d+,\s*"commenterId"')

# web_fetch._format_tracker_json renders the same Google Code comment array
# as "Comment N (YYYY-MM-DD): text" lines instead of raw JSON — the pattern
# above no longer matches that shape, so without this the truncation-at-
# second-comment safeguard silently stopped catching fix-revealing replies
# (regression found via a live Closure-150 collect: "Comment 6 ... This
# issue was closed by revision r2240." leaked into the pre-fix arm).
_FORMATTED_COMMENT_N_RE = re.compile(r"\nComment (\d+) \(")

# Meta segments that reveal post-open state on API-format report meta lines
# (e.g. "Type: Bug | Priority: Major | Status: Resolved | Resolution: Fixed").
_REPORT_META_KEYS = ("Type", "State", "Priority", "Status", "Resolution", "Labels")
_REPORT_META_DROP = ("State", "Status", "Resolution")

# Inline status/resolution tokens on flattened generic-HTML/JSON tracker pages
# (SourceForge, Google Code), which are neither a clean " | "-delimited meta
# line NOR past the comment-thread truncation point — a ticket header like
# "#868 ... Status: closed-fixed Owner: ..." precedes the description itself,
# and Google Code JSON has an unquoted-colon '"status":"Fixed"' top-level key.
# Also catches transition-log phrasing ("status : open --> closed-fixed").
# Trade-off: a rare false positive eating 1-2 incidental words beats the
# alternative of a resolved-ticket status token surviving sanitization.
_INLINE_STATUS_RE = re.compile(
    r'\bstatus"?\s*:\s*"?[\w-]+"?(?:\s*-+>\s*"?[\w-]+"?)?', re.IGNORECASE
)
_INLINE_RESOLUTION_RE = re.compile(
    r'\bresolution"?\s*:\s*"?[\w-]+"?(?:\s*-+>\s*"?[\w-]+"?)?', re.IGNORECASE
)


def _is_separator_line(line: str) -> bool:
    stripped = line.strip()
    return len(stripped) >= 10 and set(stripped) == {"-"}


# Local-machine paths and corpus-wide stats that leak into every `defects4j
# info` call — carry zero classification signal for any single bug, so
# unlike _BUG_INFO_FIX_SECTIONS these strip in BOTH arms (see
# docs/suspicious_frame_selection.md).
_BUG_INFO_NOISE_LINE_PREFIXES = (
    "script dir:",
    "base dir:",
    "major root:",
    "repo dir:",
    "commit db:",
    "number of bugs:",
)


def _strip_bug_info_noise(text: str) -> str:
    """Drop collection-machine-path / dataset-size lines from `bug_info`."""
    if not text:
        return text
    lines = [
        line for line in text.splitlines()
        if not any(line.strip().lower().startswith(prefix) for prefix in _BUG_INFO_NOISE_LINE_PREFIXES)
    ]
    return "\n".join(lines)


# Mirrors pipeline._FRAMEWORK_PREFIXES — duplicated (not imported) to avoid a
# prompting<->pipeline import cycle (pipeline.py already imports
# build_messages from this module).
_TRACE_FRAMEWORK_PREFIXES = (
    "org.junit.", "junit.", "org.hamcrest.", "org.mockito.", "org.powermock.",
    "org.easymock.", "org.assertj.", "org.apache.tools.ant.", "org.apache.maven.",
    "org.gradle.", "java.", "javax.", "jdk.", "sun.", "com.sun.", "jdk.internal.reflect.",
)

# Optional non-capturing (?:module/)? handles Java 9+ module-qualified
# frames, e.g. "at java.base/jdk.internal.reflect.NativeMethodAccessorImpl
# .invoke0(...)" — without it the "/" breaks the match entirely and the
# line falls through as unrecognized (kept instead of correctly filtered).
_TRACE_LINE_CLASS_RE = re.compile(r"^\s*at\s+(?:[\w.]+/)?([\w.$]+)\.")


def _filter_stack_trace_noise(stack_trace: list[str], limit: int) -> list[str]:
    """Keep the exception headline plus up to *limit* non-framework frame
    lines. The raw first-N-lines excerpt used to be dominated by JDK
    reflection / Ant / JUnit runner boilerplate for assertion-style failures
    (e.g. 10 of 15 lines for Closure-150) — this surfaces signal lines
    instead within the same budget."""
    if not stack_trace:
        return []
    kept = [stack_trace[0]]
    for line in stack_trace[1:]:
        match = _TRACE_LINE_CLASS_RE.match(line)
        class_name = match.group(1) if match else ""
        if class_name and any(class_name.startswith(prefix) for prefix in _TRACE_FRAMEWORK_PREFIXES):
            continue
        kept.append(line)
        if len(kept) - 1 >= limit:
            break
    return kept


def sanitize_bug_info(text: str) -> str:
    """Strip fix-derived sections from raw `defects4j info` output.

    Drops the "List of modified sources" and "Revision ID/date (fixed
    version)" sections wholesale; everything else (project summary, bug
    report id/url, triggering tests) is legitimately pre-fix and kept."""
    if not text:
        return text
    out: list[str] = []
    skipping = False
    for line in text.splitlines():
        if skipping:
            if _is_separator_line(line):
                skipping = False
                out.append(line)  # keep one delimiter between surviving sections
            continue
        header = line.strip().lower().rstrip(":")
        if header in _BUG_INFO_FIX_SECTIONS:
            # Drop the delimiter we just emitted for this section, then skip
            # until the section's closing delimiter.
            if out and _is_separator_line(out[-1]):
                out.pop()
            skipping = True
            continue
        out.append(line)
    return "\n".join(out)


def sanitize_bug_report(text: str) -> str:
    """Strip post-fix material from bug report text.

    Keeps the report as filed (title, metadata, description); removes the
    comment thread (which post-dates the report and frequently discusses the
    fix), Status/Resolution/State segments from API meta lines, and inline
    status/resolution tokens on flattened generic-HTML tracker pages."""
    if not text:
        return text
    # 1. Truncate at the earliest comment-thread marker.
    cut = len(text)
    for marker in _REPORT_COMMENT_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    # 1b. Google Code-style JSON comments[] array: keep only the first
    # (original-report) comment object.
    json_comments = list(_JSON_SECOND_COMMENT_RE.finditer(text))
    if len(json_comments) >= 2:
        cut = min(cut, json_comments[1].start())
    # 1c. Same tracker shape, but already reformatted by
    # web_fetch._format_tracker_json into "Comment N (date): text" lines —
    # keep only "Comment 0" (the original report), drop "Comment 1" onward.
    formatted_comments = list(_FORMATTED_COMMENT_N_RE.finditer(text))
    if len(formatted_comments) >= 2:
        cut = min(cut, formatted_comments[1].start())
    text = text[:cut].rstrip()
    # 2. Drop post-open segments from meta lines. Only lines whose every
    #    " | "-separated segment is a known meta key are rewritten, so
    #    description text containing pipes is never touched.
    lines = text.splitlines()
    meta_re = re.compile(r"^(%s): " % "|".join(_REPORT_META_KEYS))
    for i, line in enumerate(lines):
        segments = line.split(" | ")
        if len(segments) > 1 and all(meta_re.match(seg.strip()) for seg in segments):
            kept = [
                seg for seg in segments
                if not seg.strip().startswith(tuple(f"{key}: " for key in _REPORT_META_DROP))
            ]
            lines[i] = " | ".join(kept)
    text = "\n".join(lines).strip()
    # 3. Sweep any remaining inline status/resolution tokens — covers ticket
    #    headers on flattened generic-HTML pages that precede the truncation
    #    point (step 1 only removes the comment-thread TAIL).
    text = _INLINE_STATUS_RE.sub("", text)
    text = _INLINE_RESOLUTION_RE.sub("", text)
    return _collapse_line_whitespace(text)


def _collapse_line_whitespace(text: str) -> str:
    """Collapse runs of spaces left by token removal, without merging lines."""
    return "\n".join(" ".join(line.split()) for line in text.split("\n")).strip()


def _context_payload(context: BugContext) -> dict:
    # Filter metadata — exclude hidden oracles, and collapse the long
    # unrelated-test-class list (tests.relevant) to a count: it has no
    # bearing on ODC type/impact and was pure token bulk (23 class names for
    # a typical Closure bug). tests.trigger (the actually failing test) is
    # kept verbatim.
    filtered_metadata: dict = {}
    for key, value in context.metadata.items():
        if key == "classes.modified":
            continue
        if key == "tests.relevant" and isinstance(value, str) and value:
            count = len([t for t in value.split(";") if t.strip()])
            filtered_metadata[key] = f"{count} relevant test classes (list omitted — not diagnostic for ODC type/impact)"
            continue
        filtered_metadata[key] = value

    payload: dict = {
        "project_id": context.project_id,
        "bug_id": context.bug_id,
        "version_id": context.version_id,
        "metadata": filtered_metadata,
        "failing_tests": [],
        "suspicious_frames": [],
        "production_code_snippets": [],
        "test_code_snippets": [],
        "coverage_summary": [],
    }

    # ── Bug info / bug report ───────────────────────────────────────────
    # Fix-revealing sections sanitize in the pre-fix arm only; the
    # local-path/corpus-size noise strips in both arms (it's noise either
    # way, never fix-derived).
    prefix_arm = not context.fix_diff
    bug_info = sanitize_bug_info(context.bug_info) if prefix_arm else context.bug_info
    bug_info = _strip_bug_info_noise(bug_info)
    if bug_info:
        payload["bug_info"] = bug_info

    bug_report = (
        sanitize_bug_report(context.bug_report_content) if prefix_arm else context.bug_report_content
    )
    if bug_report:
        payload["bug_report_description"] = bug_report

    # ── Failing tests ─────────────────────────────────────────────────
    for failure in context.failures[:5]:
        payload["failing_tests"].append(
            {
                "test_name": failure.test_name,
                "headline": failure.headline,
                "stack_trace_excerpt": _filter_stack_trace_noise(failure.stack_trace, 15),
            }
        )

    # ── Suspicious frames ─────────────────────────────────────────────
    for frame in context.suspicious_frames[:10]:
        payload["suspicious_frames"].append(
            {
                "class_name": frame.class_name,
                "method_name": frame.method_name,
                "file_name": frame.file_name,
                "line_number": frame.line_number,
                "origin": frame.origin,
            }
        )

    # Both styles get the same evidence budget to avoid confounds in RQ2.2.
    # The only difference between scientific and direct is the system prompt.
    snippet_limit = 8
    prod_count = 0
    test_count = 0
    for snippet in context.code_snippets:
        is_test = snippet.reason.startswith("Test source:")
        if is_test and test_count < 3:
            payload["test_code_snippets"].append(
                {
                    "class_name": snippet.class_name,
                    "reason": snippet.reason,
                    "file_path": snippet.file_path,
                    "start_line": snippet.start_line,
                    "end_line": snippet.end_line,
                    "focus_line": snippet.focus_line,
                    "content": snippet.content,
                }
            )
            test_count += 1
        elif not is_test and prod_count < snippet_limit:
            payload["production_code_snippets"].append(
                {
                    "class_name": snippet.class_name,
                    "reason": snippet.reason,
                    "file_path": snippet.file_path,
                    "start_line": snippet.start_line,
                    "end_line": snippet.end_line,
                    "focus_line": snippet.focus_line,
                    "content": snippet.content,
                }
            )
            prod_count += 1

    # ── Coverage ──────────────────────────────────────────────────────
    # The 6 classes the failing tests executed most. context.coverage is in
    # report (≈alphabetical) order and lists every instrumented class, so the
    # old `[:6]` showed only never-executed classes for 294/431 v2 contexts.
    executed = [c for c in context.coverage if any(line.hits for line in c.covered_lines)]
    executed.sort(key=lambda c: -sum(1 for line in c.covered_lines if line.hits))
    for coverage in executed[:6]:
        payload["coverage_summary"].append(
            {
                "class_name": coverage.class_name,
                "line_rate": coverage.line_rate,
                "branch_rate": coverage.branch_rate,
                "top_covered_lines": [
                    {"line_number": line.line_number, "hits": line.hits}
                    for line in coverage.covered_lines[:10]
                ],
            }
        )
    # ── Fix diff (post-fix oracle, optional) ────────────────────────────
    if context.fix_diff:
        payload["fix_diff_oracle"] = {
            "note": "This is POST-FIX oracle information (the actual buggy→fixed diff). "
                    "Use it to confirm your classification, but remember: in a real scenario "
                    "this information would NOT be available before the fix.",
            "unified_diff": context.fix_diff,
        }

    # ── Notes ─────────────────────────────────────────────────────────
    # Deliberately NOT forwarded to the LLM: every entry pipeline.py appends
    # (compile/test/coverage exit codes, raw Ant build stderr excerpts,
    # fix-diff collection status) is collection-run bookkeeping, not bug
    # evidence — zero classification signal, pure token bulk. Kept in
    # context.json for human debugging/provenance only. See
    # docs/suspicious_frame_selection.md.

    # NOTE: the old odc_opener_hints/odc_closer_hints keyword heuristics were
    # removed (docs/odc_alignment_audit.md §4.4): they anchored the LLM's
    # opener judgments, used unsound age/qualifier rules, and leaked ODC
    # vocabulary into the zero-free baseline payload.

    return payload


def _json_contract(taxonomy_mode: str = TAXONOMY_CLOSED) -> str:
    other_fields = ""
    if taxonomy_mode == TAXONOMY_OPEN:
        other_fields = (
            '"other_justification": "REQUIRED if odc_type is Other: why each of the 7 ODC types fails, citing evidence (else omit)", '
            '"nearest_type": "REQUIRED if odc_type is Other: the closest of the 7 ODC types (else omit)", '
            '"other_confidence": "REQUIRED if odc_type is Other: number 0-1, confidence that this is a true taxonomy gap (else omit)", '
        )
    return (
        "{"
        '"odc_type": "one of the allowed ODC types", '
        + other_fields +
        '"family": "Control and Data Flow or Structural", '
        '"target": "Design/Code (optional; closer attribute)", '
        '"qualifier": "Missing or Incorrect or Extraneous (optional; closer attribute, determinable from the fix diff)", '
        '"confidence": "number between 0 and 1", '
        '"needs_human_review": "boolean", '
        '"observation_summary": "short paragraph describing failure symptoms", '
        '"reasoning_summary": "short paragraph explaining WHY this ODC type was chosen over alternatives", '
        '"evidence_used": ["specific evidence items from the input"], '
        '"evidence_gaps": ["missing evidence or ambiguity"], '
        '"alternative_types": [{"type": "ODC type", "why_not_primary": "specific reason based on evidence"}]'
        "}"
    )


def _build_zero_system_prompt(*, has_fix_diff: bool = False) -> str:
    """Build the zero-shot system prompt (free taxonomy, no worked examples).

    This prompt intentionally excludes ALL ODC concepts:
    - No ODC type names or descriptions
    - No taxonomy guidance or family groupings
    - No anti-bias rules referencing ODC types
    - No JSON schema with ODC fields
    - No diagnostic decision tree or worked examples

    This is the unstructured baseline (the retired 'naive' preset): the LLM
    classifies in its own words using the simplified JSON contract.
    """
    parts = [
        "You are a software defect analyst.",
        "Your job is to analyze a software bug and determine what TYPE of defect it is.",
    ]

    if has_fix_diff:
        parts.extend([
            "",
            "You have access to both the buggy code evidence AND the actual code change that fixed the bug.",
            "Use the fix diff to understand the NATURE of the coding error.",
        ])
    else:
        parts.extend([
            "",
            "You have access to pre-fix evidence only: failing tests, stack traces, and code snippets.",
            "Determine the root cause based on the available symptoms and code.",
        ])

    parts.extend([
        "",
        "Focus on the ROOT CAUSE of the defect, not just the observable symptom.",
        "Be specific and technical — describe the nature of the coding error.",
        "",
        "Return only valid JSON matching this schema:",
        _naive_json_contract(),
    ])
    return "\n".join(parts)


def _naive_json_contract() -> str:
    """Simplified JSON contract for naive baseline — no ODC fields."""
    return (
        "{"
        '"defect_type": "a short, specific label for the type of defect (your own words)", '
        '"confidence": "number between 0 and 100", '
        '"reasoning_summary": "a paragraph explaining your classification and what evidence supports it", '
        '"root_cause": "one sentence describing the specific coding error", '
        '"symptom": "one sentence describing the observable failure"'
        "}"
    )
