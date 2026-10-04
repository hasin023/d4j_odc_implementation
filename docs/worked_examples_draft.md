# Worked examples (approved; in the prompt since `v3-2026-10-05`)

> **Status 2026-10-05:** all 7 approved by the user and implemented verbatim as
> `prompting._WORKED_EXAMPLES` (headings renamed "### Worked example N: …", wrapped in `<example>`
> tags; a test checks order and types). Change them only with a new `PROMPT_VERSION` and a log entry.

Written 2026-10-04. These are the 7 worked examples decided in
`docs/few_shot_worked_examples_research.md` Q6, drafted as the text that would replace
`prompting.py::_few_shot_examples()`. Nothing in the code has changed yet. Terminology as in
`docs/few_shot_terminology.md`.

## How to read this file

- Each example has two parts. **Prompt text** is exactly what would go into the prompt. **Provenance**
  is for us: where each quote comes from and what was left out.
- Inside the prompt text, report and code lines are copied word for word. `[…]` marks a cut. Nothing
  inside a quote is reworded.
- **Buggy code** and **Fix** hold code only, no prose. The first line of each buggy-code block is a
  comment naming the file (and method), e.g. `// StorageService.java, ...`. That line is ours, not from
  the source.
- The **Type** and **Why not** lines are our own words. Each **Type** line quotes the
  IBM ODC v5.2 phrase from `odc.py` that fits.
- Every example uses the same six headings in the same order (Min et al. 2022, format):
  Bug report → Buggy code → Fix → Type → Why not.
- A "First reading" step was drafted and then dropped (2026-10-04): it was a guess written by us
  after seeing the fix, and the reporter's real framing is already in the Bug report line.
- Quotes are cited to the public JIRA issue and the GitHub fix commit. The Coimbra dataset (Agnelo et
  al., JSS 2020) supplies only the label and the bug choice. Its readme states no license, so ask the
  authors before publishing anything that prints these excerpts (research doc Q6.2, deferred).
- Order (Q6.1.6): Checking, Assignment/Initialization, Algorithm/Method, Interface/O-O Messages,
  Function/Class/Object, Relationship, Timing/Serialization.

## Intro line (replaces "These examples show how to distinguish between ODC types using pre-fix evidence:")

> These are solved bugs from other projects (Apache Cassandra and HBase), each labeled by ODC
> researchers. Each one shows the evidence, the real fix, and the type the fix
> points to. They show how to reason; they are not related to the bug you are classifying.

---

## Example 1: Checking (CASSANDRA-11239)

### Prompt text

````
### Example 1: Checking
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
````

### Provenance

- Report: https://issues.apache.org/jira/browse/CASSANDRA-11239 (title and description).
- Fix: https://github.com/apache/cassandra/commit/0a35341675c6c2026113736f9447f08069b6eb83
  (`src/java/org/apache/cassandra/service/StorageService.java`; `CHANGES.txt` hunk left out).
- Buggy code: same file at the parent commit `8fc1b28e83`. The 7-parameter deprecated
  `forceRepairRangeAsync(..., boolean isLocal, ...)` body, and lines from the
  `forceRepairRangeAsync(..., int parallelismDegree, ...)` body. Each piece is an unbroken run of lines;
  the `[…]` between them skips to the other method. The method signatures are left out.
- Coimbra label: Checking; second labeler agreed.
- **Why not (approved by the user 2026-10-04).** Rival Algorithm/Method: Checking's most frequent
  confusion is with Algorithm (Henningsson & Wohlin 2004, Table 6: CH–AL 68 occasions; tier 2), and
  Checking ↔ Algorithm/Method is our least stable boundary, with an added branch pulling Math_17 to
  Algorithm (manual analysis README findings 7, 9; tier 3). Reason: the IBM Checking definition quoted
  verbatim (tier 1); "no computation is implemented or changed" applies IBM's Algorithm definition to
  the diff (Claude's reading, approved). The earlier rival, Interface, was Claude's own pick and was
  dropped.

---

## Example 2: Assignment/Initialization (HBASE-12976)

### Prompt text

````
### Example 2: Assignment/Initialization
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
````

### Provenance

- Report: https://issues.apache.org/jira/browse/HBASE-12976 (title, description, comment #14306701).
  The description's grammar ("I propose we hbase.client...") is the reporter's, kept as is.
- Fix: https://github.com/apache/hbase/commit/2583e8de574ae4b002c5dbc80b0da666b42dd699
  (`hbase-common/src/main/java/org/apache/hadoop/hbase/HConstants.java`). Left out: the Javadoc line
  change ("unlimited" → "2MB") and the whole `hbase-default.xml` hunk. That hunk is a configuration
  file; in ODC a config change is a different Target, not a defect type (`docs/other_category.md` §1).
- Buggy code: `HConstants.java` at the parent commit `96cdc7987e`, lines 614–616.
- Note: the report reads as a tuning proposal more than a crash. The symptom (OOMs, full GCs) is in
  the description and the first comment.
- Coimbra label: Assignment/Initialization; second labeler agreed.
- **Why not (approved by the user 2026-10-04).** Rival Algorithm/Method: named in IBM's own Assignment
  definition (tier 1); AS–AL is the top confusion, 184 occasions (Henningsson & Wohlin 2004, Table 6;
  tier 2); Coimbra's convention that multiple Assignment corrections become Algorithm (Agnelo et al.
  §IV.A; tier 2); Algorithm ↔ Assignment is our second least stable boundary (manual analysis finding 9;
  tier 3). Reason: IBM quote plus what the diff shows. Removed: "the scanner already enforces this limit
  correctly" (scanner code never read). Type line: "Initialization of parameters" for a setting's
  default value is Claude's reading of IBM illustration (2), approved.

---

## Example 3: Algorithm/Method (CASSANDRA-7508)

### Prompt text

````
### Example 3: Algorithm/Method
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
````

### Provenance

- Report: https://issues.apache.org/jira/browse/CASSANDRA-7508 (title and description; the description
  is a single pasted console line, cut with `[…]`). Comment #14062575 confirms the approach: "uses the
  actual token/endpoint map to determine if vnodes are enabled instead of using the conf, which
  nodetool shouldn't have been doing anyway."
- Fix: the original 2.1 commit
  https://github.com/apache/cassandra/commit/721afaead6bdf02107a88f650edf1be5b1127268
  (`src/java/org/apache/cassandra/tools/NodeTool.java`). Left out: the removed
  `import org.apache.cassandra.config.DatabaseDescriptor;` line and `CHANGES.txt`.
- This replaces the 2.0 backport `74f3204c66` (`NodeCmd.java`) recorded earlier in the research doc
  §5.6. Same change, but the report's stack trace names `NodeTool$Ring.execute(NodeTool.java:464)`, and
  in `721afaead6` the removed `if (DatabaseDescriptor.getNumTokens() > 1)` is old line 464 (hunk
  `@@ -461,7` starts at 461; the `-` line is its 4th line). So the trace and the fix match.
- Buggy code: the context lines of the same hunks (the parent's version of `Ring.execute`).
- Coimbra label: Algorithm/Method; second labeler agreed.
- **Type / Why not (approved by the user 2026-10-04).** Two rivals, each with a manual-analysis
  precedent: Checking (the fix edits an `if`; CH↔ALG is our least stable boundary, finding 9;
  Henningsson & Wohlin CH–AL 68) and Assignment/Initialization (a new variable in the diff pulled
  Math_23 to Assignment, finding 7; H&W AS–AL 184). "Validates no parameter or data" and "no existing
  value was wrong" apply the IBM Checking / Assignment definitions to the diff (Claude's reading,
  approved). Old wording "counting tokens" was wrong (the loop detects a repeated endpoint) and was fixed.
- **Interface added as a third rival (approved by the user 2026-10-04, after reviewing Example 4).**
  H&W IN–AL 77. Pre-fix, the evidence points to Interface: the stack trace ends at the call
  `DatabaseDescriptor.getNumTokens()` from `NodeTool$Ring.execute`, so "nodetool calls the wrong thing" is
  a natural reading; only the fix shows Algorithm. That is the manual analysis's "right mechanism, wrong
  label" failure (finding 5), and it pairs with Example 4: correcting a call is Interface, replacing it
  with a computation is Algorithm. Basis for the line: `probe.getTokenToEndpointMap()` is unchanged context in the diff, and no
  `DatabaseDescriptor` use remains (import removed). Counterpoint: IBM Interface illustration (3)
  "incorrectly specifies the name of a service", and the issue comment "which nodetool shouldn't have
  been doing anyway", hint at a module-boundary reading.

---

## Example 4: Interface/O-O Messages (CASSANDRA-13119)

### Prompt text

````
### Example 4: Interface/O-O Messages
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
````

### Provenance

- Report: https://issues.apache.org/jira/browse/CASSANDRA-13119 (title and description). Comment
  #15994856 notes the same fix was applied to 3.0+ under CASSANDRA-13410.
- Fix: https://github.com/apache/cassandra/commit/6c5ea192c75072ba3f7369dfc23592d6ed0c319f
  (`src/java/org/apache/cassandra/tools/nodetool/UpgradeSSTable.java`). Left out: the end-of-file
  newline change and `CHANGES.txt`.
- Buggy code: `src/java/org/apache/cassandra/tools/NodeTool.java` at the parent commit `868be9c283`,
  lines 315–325 (`[…]` cuts lines 322–324).
- Coimbra label: Interface/O-O Messages; second labeler agreed.
- **Type / Why not (approved by the user 2026-10-04).** Rivals: Function/Class/Object (the report frames
  a missing feature, and a report's proposal tends to become the label: manual analysis finding 8,
  Math_90; tier 3) and Assignment/Initialization (a literal `true` is passed, IBM lists "Initialization of
  parameters" under Assignment; H&W AS–IN 59; tiers 1, 2). Not used: H&W's top Interface confusion IN–AL
  77, since nothing in this diff looks algorithmic. IBM Interface illustration (4) ("number and/or types
  of parameters … do not conform with the signature") was considered and dropped: the 2-parameter call
  does match a real signature, so the fit is a stretch.

---

## Example 5: Function/Class/Object (CASSANDRA-6378)

Replaced CASSANDRA-5752 on 2026-10-04 (user's decision): 5752's label rested on a contestable
"design change" reading and its fix was hard to excerpt. 5752 is kept in the research doc as a rejected
candidate.

### Prompt text

````
### Example 5: Function/Class/Object
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
````

### Provenance

- Report: https://issues.apache.org/jira/browse/CASSANDRA-6378 (title and description; the stack trace
  is cut to its first and its "Caused by" frame). Comment #13852268: "The entire SSLTransportFactory.java
  is missed in the commit", hence two commits.
- Fix, commit 1: https://github.com/apache/cassandra/commit/1b2a190379 (`src/java/org/apache/cassandra/tools/BulkLoader.java`;
  `CHANGES.txt` left out). Left out: 9 option-name constants, the `ExternalClient` constructor and field
  change, the option parsing, `getTransportFactory()`, `configureTransportFactory()`, and 7 of the 10
  `addOption` lines.
- Fix, commit 2: https://github.com/apache/cassandra/commit/4a6f8a6610 ("add SSLTransportFactory.java",
  new file, 86 lines). Shown: class declaration and the start of `openTransport()`.
- Buggy code: `BulkLoader.java` at the parent of commit 1, `21bb531460`, lines 236–240.
- The hex reading: 352518400 = 0x15030100. In the TLS record format (RFC 5246 §6.2.1) byte 0x15 (21) is
  content type "alert" and 0x03 0x01 is protocol version TLS 1.0, so the server answered with a TLS
  record. Computed 2026-10-04.
- Coimbra label: Function/Class/Object / Missing (`Cassandra after.csv`); checked by external
  researcher 3 (`verificacao-researcher3-410.xlsm`, sheet `Planilha1`, row 238), who also gave
  Function/Class/Object.
- **Type / Why not (approved by the user 2026-10-05).** Two rivals: Algorithm/Method (IBM's own
  design-change split between the two definitions; tier 1) and Interface/O-O Messages (the fix's visible
  change outside the new class is a parameter added to `createThriftClient`, the kind of diff surface
  form that misled post-fix runs, manual analysis finding 7; tier 3). "No existing call was wrong": the
  buggy file has one call to `createThriftClient` (line 197) and the fix only adds the new argument.
  Henningsson & Wohlin give no FCO confusion data.
- **Assignment/Initialization considered and dropped (user's point, 2026-10-05).** The error says "max
  length", but Cassandra's code sets no limit: 16384000 is `DEFAULT_MAX_LENGTH` inside Thrift 0.9.1
  (`TFramedTransport.java`), used because the buggy code calls `new TFramedTransport(socket)`. The only
  way to change it from Cassandra's code is the other constructor, `new TFramedTransport(socket,
  maxLength)`: a different parameter list, i.e. Interface, not Assignment. So Assignment fits from no
  angle, and the Interface line covers that temptation too.
- **Background only, not in the prompt:** why the error appears. The report and comments do not explain
  it. Claude's reading: the server required TLS, the loader connected plain, and Thrift's plain transport
  read the first 4 bytes of the server's TLS reply as a length. 352518400 = hex 15 03 01 00; in the TLS
  record format (RFC 5246 §6.2.1) 0x15 is "alert" and 0x03 0x01 is TLS 1.0. The same symptom with
  encryption on is reported in CASSANDRA-10445 (https://issues.apache.org/jira/browse/CASSANDRA-10445,
  "Frame size (352518912) larger than max length (15728640)!", = 15 03 03 00), which does not explain
  the cause either.
---

## Example 6: Relationship (CASSANDRA-9055)

### Prompt text

````
### Example 6: Relationship
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
````

### Provenance

- Report: https://issues.apache.org/jira/browse/CASSANDRA-9055 (title and description).
- Fix: https://github.com/apache/cassandra/commit/f79f80e6c80e77c081b30aabdb3af93b057154a6
  (`src/java/org/apache/cassandra/exceptions/FunctionExecutionException.java`; `CHANGES.txt` left out).
- Buggy code: `src/java/org/apache/cassandra/transport/messages/QueryMessage.java` at the parent commit
  `edcf9257ef`, lines 128–132; the class declaration is the `-` line of the fix.
- Matches IBM §4.2.1.7 illustration 2 (decided 2026-10-04, research doc 5.5).
- Coimbra label: Relationship; second labeler agreed. The only checked Relationship record with a fix
  commit, so there is no checked backup.
- **Type, no "Why not" (approved by the user 2026-10-05).** The user's reason: the bug report states the
  cause so clearly that no other type matches it, so no rival needs ruling out. This is the only example
  without a "Why not" line. Type line: both IBM Relationship illustrations, verbatim (tier 1), plus facts
  from the buggy code and diff.
- **Rival considered and dropped: Checking** (Claude's reading only): one could add the exception to the
  `instanceof` condition, but the report names the right fix and the diff contains no `if`.
- **Head-to-head with HBASE-5172** (single-labeled; `interface HTableInterface extends Closeable`, fits IBM
  illustration 2; `close()` was already declared, so it had a sourced "Why not Interface"). 9055 chosen:
  checked, fits two IBM illustrations, its report describes behaviour, and the dependent code is quotable.
  All 8 Coimbra Relationship records were reviewed (research doc 5.6).

---

## Example 7: Timing/Serialization (CASSANDRA-4255)

### Prompt text

````
### Example 7: Timing/Serialization
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
````

### Provenance

- Report: https://issues.apache.org/jira/browse/CASSANDRA-4255 (title and description; the stack trace is
  cut after its first 5 frames, the rest are JMX/RMI frames). Comment #13278113: "copyOnWriteArrayList
  would probably work too, but we already synchronize other accesses (to prevent cross-level races) so
  that's simplest here."
- Fix: https://github.com/apache/cassandra/commit/641b021d3c820c7ef8edd698554a7fc44c6ce9f3
  (`src/java/org/apache/cassandra/db/compaction/LeveledManifest.java`; `CHANGES.txt` left out).
- Buggy code: `LeveledManifest.java` at the parent commit `48438ffc61`: method declarations at lines
  132, 154, 189 (`getCompactionCandidates()` and `serialize()` are synchronized too, left out), and
  `getEstimatedTasks()` from line 448. The method declaration lines are shown without their bodies.
- Coimbra label: Timing/Serialization; second labeler agreed.
- **Type / Why not (approved by the user 2026-10-05).** Type: IBM Timing definition verbatim (tier 1);
  IBM illustration (1) "Serialization is missing when making updates to a shared control block" was
  dropped because the updates (`add`, `promote`, `replace`) were already serialized and the unprotected
  method only reads. Rival Algorithm/Method: the reporter's own suggestion (CopyOnWriteArrayList) plus
  IBM Algorithm's "local data structure" (tier 1), and a fix proposed in the report tends to become the
  label (manual analysis finding 8; tier 3). Reason: the diff, IBM §4.2 "the actual correction that was
  made", and the committer's comment quoted above.
- Cuts made visible on review: the report quote now starts with `[…]` (the original opens "came across
  this, will try to figure a way to systematically reprod this. But the problem is…"), and `[…]` now
  separates the three `synchronized` declarations (lines 132, 154, 189 are not consecutive).
- Line numbers: the trace says `LeveledManifest.java:435`, but at the fix's parent `48438ffc61` the
  `getTotalBytes` call is line 454. The reporter ran an earlier build; same method and call.
- Alternatives reviewed: all 16 Java Timing records (research doc 5.6); runner-up CASSANDRA-5244.

---

## Size

Recomputed 2026-10-05 after all 7 were approved: 194 lines, roughly 3,306 tokens of prompt text
(per example: 28, 16, 28, 27, 40, 21, 34 lines). The old 5 invented worked examples were about 35 lines.
