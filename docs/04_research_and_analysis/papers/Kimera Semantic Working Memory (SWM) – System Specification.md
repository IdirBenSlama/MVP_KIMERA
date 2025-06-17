
Interactive Interfaces: Expose clear interaction surfaces (APIs or message interfaces) for external
modules (such as reasoning engines, learning algorithms, or user interfaces) to store new
knowledge, query existing memory, and subscribe to memory events. These interfaces enforce rules
for communication to maintain memory integrity (for example, requiring structured data format for
input).
Scalability and Performance: Ensure the design can scale to handle large volumes of knowledge
(millions of facts/nodes) and high throughput of updates/queries. Strategies include using efficient
data indexes (for semantic similarity search, graph traversal, etc.), distributing the memory store if
needed, and tuning the entropy evaluation to avoid bottlenecks. The system should meet
performance requirements (e.g. query latency under certain milliseconds) for real-time use cases.
Security and Integrity: Safeguard the memory content through access control and validation. Only
authorized components can modify or retrieve certain knowledge, and the system validates inputs
(to prevent malformed or malicious data from corrupting memory). The contradiction resolution
process also serves to maintain integrity by preventing inconsistent or false data from propagating
unverified.
System Overview
Kimera SWM is organized into a set of interrelated components that together realize a semantic working
memory. Figure 1 below illustrates the conceptual architecture and data flow for how information is
ingested, processed, and stored in the system (from left to right):
External Inputs: New information (facts, observations, or assertions) enters the system through
defined interfaces. Inputs could originate from natural language inputs, sensor data interpreted into
symbolic form, or other modules in an AI agent. Rather than storing the raw input, SWM
immediately processes it into an internal semantic representation.
Semantic Modeling & Encoding: The Semantic Modeler module parses and encodes incoming
data into the SWM’s internal representation. This involves identifying the key concepts, entities, and
relationships in the input and generating a vectorized or graph-based representation. For textual
inputs, this module may use a trained language model or embedding model to produce a semantic
vector (embedding) that captures the meaning without storing exact tokens. Simultaneously, it can
extract symbolic triples or frames (e.g. subject–predicate–object) to anchor the fact in a knowledge
graph structure. The outcome is a semantic encoding of the input: for example, an input sentence
"Alice is young" might be encoded as an entity node Alice with an attribute age_group=young ,
along with an embedding vector for the concept of “Alice being young”.
Entropy & Novelty Analysis: The encoded information is then evaluated by the Entropy Analyzer
component. This analyzer computes an entropy-based measure of the information content and
novelty of the incoming knowledge. It does so by comparing the new representation against existing
memory:
Novelty Check: The system queries the memory store (via the retrieval interface) to see if a similar or
identical piece of information already exists. If the new data is essentially a repeat of known
information, its novelty is low (and the system might simply reinforce the existing memory rather
than add a duplicate). If it introduces new relationships or significantly extends a concept, its novelty
is high.
Entropy Calculation: The system estimates semantic entropy for the new information. Conceptually,
this measures how unpredictable or uncertain the information is given what the system already
knows. For instance, if the system was unsure about Alice’s age and held conflicting evidence, a new
•
•
•
•
•
•
•
•
2
neighbors – structure for efficiency) embodies the semantic memory aspect, allowing flexible recall
of related knowledge by meaning.
Memory Segmentation: The store can conceptually be split into working memory vs. long-term
memory zones. Recent or highly relevant knowledge might reside in a fast in-memory cache (the
working memory portion), while older or less frequently used knowledge is kept in long-term
storage (e.g. on disk or in a database) and loaded on demand. The system may periodically
consolidate or prune the working memory to manage capacity, using entropy as a criterion (e.g.
remove or archive facts that haven’t been used recently and have low information value).
Persistence Model: All memory updates are written through to a persistent storage subsystem
(described below) to ensure durability. The memory store is effectively a layered system: an in-
memory graph and index for fast operations, synchronized with a persistent database or file storage
that can recover the entire state after a restart or failure.
Internal Communication and Control: The above components interact through a controlled
internal messaging or API calls managed by a Memory Orchestrator (or controller). This
orchestration logic ensures the steps occur in the correct sequence and enforces communication
rules:
New inputs must flow through the semantic modeler and conflict checker before reaching the
memory store. Direct insertion into memory is not allowed, preventing unvalidated data from
corrupting the knowledge base.
The orchestrator triggers the Entropy Analyzer and Contradiction Detector for each new piece of
data and waits for their assessment. Only after they signal "no conflict" or after successful resolution
does the orchestrator proceed to commit the data to the store.
The modules communicate via defined interfaces (function calls or asynchronous events). For
instance, the Semantic Modeler will output a data structure (e.g. a JSON with extracted entities and a
vector embedding) to the orchestrator, which then calls the Entropy Analyzer with that data and
current memory snapshot.
Internal APIs: Each subsystem exposes an internal API: e.g., checkContradiction(new_fact)
returns either "no conflict" or details of conflict; resolveConflict(factA, factB) returns a
reconciled fact or decision; store.commit(fact) writes to memory;
store.query(query_params) returns matching knowledge. These APIs are used internally and
are also the basis for external interaction surfaces (with appropriate security checks when called
from outside).
The communication rules also cover error handling: if a subsystem fails to respond or encounters an
error (e.g., the embedding model fails to encode the input), the orchestrator can apply fallback logic
(described later in Operational Constraints) such as retrying or storing the data in a raw form for later
processing.
The architecture described above can be implemented using existing frameworks and modules, chosen to
meet the system requirements: - External Libraries/Frameworks: Kimera SWM’s design does not mandate
proprietary technology; it can leverage standard tools. For example, the Semantic Modeler might use a
transformer-based language model (like BERT or GPT embeddings) to compute semantic vectors, using a
library such as PyTorch or TensorFlow for model inference. The knowledge graph can be managed by a
graph database or an in-memory graph library (like Neo4j, JanusGraph, or even a custom data structure).
The persistent store could be a NoSQL database or a graph store that supports ACID transactions for
reliability. If high performance similarity search is needed, an external vector database (like FAISS, Milvus, or
ElasticSearch with vector indices) can be used for the vector index. These external components provide
proven scalability and can be integrated via their APIs or drivers. - Dependency Clarification: No external
module is blindly relied upon for logic; all critical operations (entropy calculation, contradiction logic) are
•
•
•
•
•
•
•
•
5
under SWM’s control or supervision. External frameworks are used as underlying engines (for storage or
computation) to speed up development. For instance, using a graph database would handle low-level data
management, while SWM defines the schema and consistency rules on top of it. - Interaction Surfaces:
Kimera SWM exposes a well-defined external interface (likely as a library API or a service endpoint). External
systems (such as an AI agent’s dialogue manager or a user-facing application) use this interface to interact
with memory: - Knowledge Insertion API: e.g. AddFact(entity, relation, value, [context]) or
StoreKnowledge(statement) . This interface accepts structured input (ensuring the caller provides at
least an entity or semantic embedding). Free-form text might be accepted but would be internally run
through the semantic modeler to produce the structure. - Query API: e.g. Query(entity) to retrieve all
facts about an entity, or QuerySemantic(vector or text query) for a semantic search returning the
most relevant knowledge. The API might allow specifying whether an exact lookup or a similarity search is
desired. Results are returned in structured form (e.g. facts/triples with confidence scores or similarity
scores). - Subscription/Notification: Optionally, SWM could allow components to subscribe to certain memory
events (for example, "notify me if any fact about Alice changes" or "when a contradiction is resolved, send
an alert"). This can be implemented via callback hooks or messaging. - These interaction surfaces ensure
the rest of the system using SWM remains decoupled from internal implementation. They also enforce that
any data coming in or out is validated and formatted properly, contributing to security.
In summary, the System Overview provides a blueprint of how Kimera SWM ingests knowledge, represents
it semantically, uses entropy to guide processing, checks for contradictions, resolves them, and stores
information in a non-token-based semantic memory store. The modular architecture and use of selective
external frameworks ensure that the system is implementable with current technologies and can be scaled
and tested component-wise.
Subsystem Specifications
Below, each major subsystem of Kimera SWM is detailed with its responsibilities, internal design, and
interactions with other components:
1. Semantic Modeling & Encoding Subsystem
Responsibilities: This subsystem is responsible for interpreting raw input data and converting it into the
internal semantic representation of SWM. It performs parsing, concept extraction, and encoding of
meaning: - Input Handling: Accepts input in various forms (natural language text, structured data from
sensors or databases, etc.). It normalizes the input format (e.g., converting text to a standard string,
ensuring data fields are typed correctly) before processing. - Natural Language Processing (if applicable):
If the input is unstructured text, this module uses NLP techniques to parse it. This could involve: - Named
Entity Recognition (to find entity names like persons, places), - Relation Extraction (to identify relationships
expressed in the sentence), - Coreference resolution (to handle pronouns or references), - Dependency or
semantic parsing (to understand the grammatical structure, if needed for complex sentences). - Semantic
Vector Encoding: The subsystem generates a semantic embedding for the input content. This is done via
a pre-trained language model or embedding model (external module). For instance, it might feed the
sentence into a transformer model to obtain a sentence-level embedding vector. The vector captures the
gist of the statement in a high-dimensional space. The subsystem may also produce separate embeddings
for key components (e.g. one for the subject entity, one for the object) if that aids downstream tasks like
conflict checking. - Symbolic Structure Extraction: In parallel with embedding, the modeler constructs a
symbolic representation (non-token-based) of the content: - It identifies the entities involved (e.g. "Alice" as
6
an entity of type Person). - It identifies the predicate/relation (e.g. "is young" corresponds to a predicate
age_group or an attribute value). - It forms a candidate triple or node-attribute set: e.g. ( Alice --
age_group --> young ). In a knowledge graph context, Alice is a node, age_group is an edge label
(or property key), and young might be a value node or literal. - If the input is an assertion with an implicit
truth value (most facts), it assumes it to be true unless accompanied by a negation or uncertainty marker
(which would also be parsed). - The subsystem may consult a schema or ontology to correctly categorize the
relation (for example, knowing that "young" relates to age and perhaps mapping it onto an age range or
category). - Semantic Entropy Encoding: As part of encoding, the subsystem can produce a representation
of uncertainty. For example, if the input itself contains uncertainty ("Alice might be young"), it can attach a
probability or confidence to the fact (like 0.6 probability that Alice is young). This initial measure contributes
to entropy calculation. If the input is a definitive statement, initial entropy is low from the input's
perspective (though overall entropy will also depend on prior knowledge). - Output: The result is an
Encoded Knowledge Object, which might be a composite structure containing: - The graph-ready elements
(node and relation descriptors), - The embedding vector(s), - Metadata (source of the info, timestamp,
confidence score from input parsing, etc.). - Example: Input: "Alice is 25 years old as of 2023." - The
subsystem identifies "Alice" (Person entity), a relation "age" or "hasAge", value "25", and context time
"2023". - It generates an embedding for the sentence meaning, perhaps another for just ("Alice", "25 years
old"). - It produces an object: {entity: Alice, attribute: age, value: 25, unit: years,
timestamp: 2023, embedding: [vector], source: "user_input", confidence: 0.95} . -
Interactions: This subsystem interacts only upstream with external input and downstream passes its output
to the Entropy/Novelty analysis. It does not write to the memory store directly. This ensures a separation: all
input must be processed and validated here before affecting memory.
2. Entropy Analysis & Novelty Detection Subsystem
Responsibilities: This module evaluates the output of the Semantic Modeler to determine how it fits into or
deviates from existing memory, using information-theoretic measures and novelty heuristics: - Novelty
Detection: Upon receiving a new Encoded Knowledge Object, the subsystem queries the Semantic Memory
Store (via its query interface) to see if this or similar knowledge already exists: - If an identical fact exists
(same subject, relation, and value) and is marked as current/valid, the novelty is zero. The subsystem might
then decide not to re-store it; instead, it could trigger the memory store to update a usage count or refresh
the timestamp of that fact (to mark that it was encountered again). Alternatively, it may still forward it but
mark it as redundant. - If a closely related fact exists (e.g. same subject and relation but slightly different
value, or same subject and similar relation), novelty is moderate. The subsystem flags it as a potential
variant of known information, which might be an update or a conflict – in either case, further checks are
needed (this overlaps with contradiction detection). - If no related information is found, novelty is high – this
is new ground for the memory. High novelty data gets full processing (it will go through contradiction
detection too, though if nothing related exists, contradiction check will trivially pass). - Entropy Calculation:
The subsystem computes a semantic entropy score for the new information, which quantifies the
unpredictability of this information given what is stored: - It may model the memory as a probabilistic
distribution over certain variables. For instance, if the memory holds a probability distribution for the age of
Alice (perhaps it had two possible ages with some probabilities), the entropy of that distribution indicates
uncertainty. A new specific age value for Alice would reduce entropy – the difference (information gain) can
be measured by Kullback-Leibler divergence or simply entropy reduction. - If memory isn’t explicitly
probabilistic, another approach is to generate multiple hypothetical interpretations of the new info and see
how consistent they are. In an LLM-driven scenario, one might sample multiple paraphrases or answers and
cluster them to estimate semantic entropy . In SWM’s context, this could translate to checking how many1
7
embedding of the new fact to find any stored facts that are semantically opposite. For example, if the new
fact embedding is very close (but maybe negatively correlated) to an existing fact’s embedding, that could
indicate they are opposite statements. One practical method: store, for certain facts, a precomputed
"negation vector" or an attribute that indicates the logical negation. The detector can then quickly see if an
entity has both a property and its negation asserted. - Conflict Identification: Once relevant knowledge is
retrieved, the subsystem applies rules to determine if a true conflict exists: - For binary or boolean
attributes (e.g. "isAlive" true/false), any disagreement is a direct contradiction. - For numeric or categorical
data, a conflict could be a discrepancy outside allowed tolerances (like ages differing significantly or an
object classified in two categories that are disjoint). - For text or conceptual info, it might rely on a
predefined list of antonyms or a model to determine oppositeness (like "X is A" vs "X is not A" or "X is B"
where B is known to contradict A). - The subsystem must also ensure it’s comparing statements in the same
context. For example, "Alice was young in 1990" vs "Alice is old in 2023" are not actually contradictory, they
are time-specific. Context fields (like timestamps or location) are used to differentiate statements; a conflict
is flagged only if they purport to be true in overlapping contexts. - False Positive Mitigation: It’s important
that the detector not misclassify new info as a contradiction when it’s actually complementary. The system
can be configured with constraints or ontology info to avoid this. For instance, if two facts are about
different aspects of an entity (Alice’s age vs Alice’s location), they are not in conflict. Or if the contradiction is
only superficial (like synonyms), the semantic comparison should catch that they are actually consistent
(e.g. "Alice is young" vs "Alice is youthful" should not be flagged because they mean the same thing). -
Efficiency Considerations: Contradiction checking should ideally be scoped to relevant memory to avoid
scanning the entire knowledge base for every insertion. The memory store can maintain a per-entity index
of current facts, and possibly a negation index (index of all negative statements). This way the detector can
retrieve just the entries for "Alice" to check for contradictions about Alice. - Output: The detector outputs
either: - A no-conflict signal (with perhaps a summary "no inconsistency found") which tells the
orchestrator it’s safe to commit the knowledge to memory. - Or a conflict report containing details of what
it found. This report will include references to the conflicting memory items and the nature of the conflict
(e.g. value mismatch, logical negation, etc.). It hands this to the Contradiction Resolution subsystem for
handling. - Testing: This subsystem can be tested with a variety of scenarios: - Simple direct conflicts (store
a fact, then input a direct opposite, see if it flags it). - No-conflict cases that are similar (input redundant fact
or a related but not contradictory fact, ensure it does not flag). - Edge cases with context (same facts
different context should not conflict, conflicting facts same context should conflict). - Performance tests
ensuring it can handle checking even when an entity has many facts. - Relation to Entropy: Often, a
contradiction implies high entropy (uncertainty) about that piece of knowledge in the system. The
subsystem may feed back into the entropy model: e.g., if a contradiction is found, the memory entries
involved might have their entropy scores increased (since now there’s ambiguity). This coupling means after
resolution, the entropy can drop once the ambiguity is resolved.
4. Contradiction Resolution Subsystem
Responsibilities: This subsystem takes the conflict report from the detector and executes a strategy to
resolve the inconsistency while preserving as much valid information as possible. It ensures the memory’s
consistency by either eliminating the contradiction or encoding it in a way that’s logically coherent. -
Resolution Strategies: The subsystem implements multiple resolution rules (as mentioned in the
overview) which can be invoked depending on the scenario: 1. Update/Override: If temporal ordering or
source reliability clearly favors one fact, the subsystem will update the memory: the favored fact remains or
is inserted, and the disfavored fact is marked as invalidated or moved to an archive. For example: - Newer
information overrides older: The older memory entry might get a flag superseded=true or moved to a
9
hashmaps for node lookups, etc.). - For very high throughput, we might implement batch operations (e.g.,
queue multiple new facts and then write them in one transaction or in bulk to the DB). - The subsystem
should also monitor its size and maybe performance metrics (like average query time) to know when to
suggest scaling (e.g., splitting data or upgrading hardware). - Testability: We can test the memory store by
itself with known inputs: insert some facts, query them, update, query again, etc., verifying correct storage
and retrieval. Also test persistence by simulating a shutdown: after inserts, save state, then reload and
ensure all data is present and indexes reconstructed correctly.
6. Internal Communication & Orchestration Subsystem
Responsibilities: Although not always a separately coded module, the orchestration logic is critical. It
manages the workflow between the above subsystems and enforces internal communication rules: -
Control Flow: On receiving a new input (via external API or internal trigger), the orchestrator calls each
subsystem in the required order: 1. SemanticModel.encode(input) → produces encoded knowledge
object. 2. EntropyAnalyzer.evaluate(new_object) → returns annotated object (with novelty/
entropy) and a decision to proceed or not. 3. If proceed, ContradictionDetector.check(new_object)
→ returns either "no conflict" or a conflict report. 4. If conflict report, call
ContradictionResolver.resolve(conflict_report) → gets resolution outcome (which may modify
new_object or indicate to abort storing). 5. If resolution outcome is to store (either updated object or
original if no conflict), call MemoryStore.add(resolved_object) . 6. If resolution outcome is not to
store (e.g., it was a duplicate or invalidated by conflict), then skip storing or possibly remove something if
needed. 7. Acknowledge completion back to the source (maybe via API response "stored successfully" or
"not stored due to conflict with X"). - Event Bus: Optionally, the system can be event-driven. The
orchestrator could publish events like "new_fact_encoded", "conflict_detected", "conflict_resolved",
"fact_committed". Each subsystem could subscribe to events rather than being directly invoked. This
decouples modules further and allows, for example, the Contradiction Detector to continuously watch both
new inputs and even changes in memory (in case conflicts could arise from merging knowledge, though
usually conflict arises only on new insertion). - The use of an internal event bus (like in-process pub-sub or
an actor model) could improve scalability (different components can run on different threads or nodes).
However, it adds complexity in ensuring ordering (we must ensure encoding happens before detection, etc.,
which can be managed by event sequence or dependencies). - For now, a simpler sequential orchestration
(which could still be multi-threaded but with locks around memory operations) might suffice and is easier to
test deterministically. - Error Handling: The orchestrator implements fallback logic for subsystem failures: -
If the Semantic Modeler fails (e.g., the external model service times out or throws an error), the
orchestrator can catch that. Fallback might be to retry encoding (maybe once or twice), or degrade to a
simpler encoding method (perhaps use a simpler rule-based parse if the ML model fails). If neither works,
the orchestrator may log an error and reject that input (or store it in a raw text form tagged as
"unprocessed input" so that it’s not lost entirely – this depends on requirements). - If the Entropy Analyzer
fails or returns an inconclusive result (maybe the calculation encountered an edge case), the orchestrator
can choose a safe default: e.g., treat the input as novel (to ensure it's at least considered) but perhaps flag it
with a warning. Or it might skip entropy analysis and go straight to contradiction checking to be safe
(ensuring consistency even if we couldn’t measure surprise). - If the Contradiction Detector fails (e.g.,
query to memory store fails or some logic error), the orchestrator should not blindly commit the new info,
because it might introduce inconsistency. A prudent fallback is to hold off storing the knowledge and mark
it as needing manual review. Alternatively, if the system design allows, it could attempt a simpler conflict
check (like a basic exact match check as a minimum) to at least avoid obvious duplicates, then store
tentatively. However, storing without full conflict check can be risky – better to fail safe (do not store
13
applied. 6. If Alice was not found, the system might return a not-found response or an empty result.
Optionally, semantic similarity could be used to guess maybe the user meant someone with a similar name
– but that goes into semantic query territory.
2. Semantic Search Query:
Now consider a more complex query: "Who is Alice’s brother?" The user might call an API like GET /memory/
query?question="Who is Alice's brother" . If the interface supports natural language queries, it
will need to interpret this. Likely, it will: 1. The External Interface passes the question to the Semantic
Modeler (similar to how it handles an input sentence). The modeler encodes the query into a semantic
form. For instance, it identifies that the question asks for a person who is brother of Alice. It might produce
an internal query representation like: {relation: sibling, entity: Alice, find: OtherEntity
WHERE OtherEntity gender = male} (the gender part might come from interpreting 'brother'). It also
creates an embedding for the query meaning. 2. The orchestrator then uses the Memory Store to answer
the query. There are two possible approaches and the system might use both: - Symbolic Graph Query:
Using the structured form, the orchestrator asks the memory store: "Find all entities that have relation
sibling with Alice". The memory returns Bob (from earlier, since we stored Bob as Alice’s sibling). It
might also check Bob’s metadata to confirm gender if strictly looking for 'brother'; if the data model
encoded Bob as male, then Bob qualifies as brother. If not, and if the system considers any sibling as a valid
answer to 'brother', it might just return Bob anyway. - Semantic Vector Query: Additionally, the
orchestrator might perform a vector search using the query embedding. It looks for vectors similar to the
query in the vector index. The embedding for "Alice's brother" should closely match the embedding stored
for the fact "Bob is Alice's brother" or "Alice sibling Bob". The vector search likely brings up Bob-Alice sibling
fact as a top hit. If the memory had multiple siblings for Alice, they might all come up. 3. The results from
symbolic and semantic search are merged (de-duplicated if they overlap). Symbolic ensures precision (direct
knowledge) and semantic ensures recall (in case the question was phrased oddly or the relation needed
inference). 4. The result (Bob's identity as Alice’s brother) is then formatted by the interface. It could simply
output "Bob", or a sentence if the interface does answer generation (but generation is outside SWM’s scope
—SWM would typically just give the data, not a natural language sentence). 5. The user/program receives
the answer. 6. Post query events: The system might log the query for analytics or increment some usage
counters in memory (like “Alice’s data was accessed X times”). If an answer wasn’t found, the system could
even trigger a learning mechanism (like an intrinsic goal to find out that info if it’s critical, but that again is
outside pure memory – more an agent behavior).
Complex Query Example: If a query is more abstract like "How many siblings does Alice have?", the
interface might break it down or use an external reasoner. SWM itself can answer if it’s capable of simple
aggregation: it would fetch Alice’s siblings list and count them. If not, an external logic would do that after
retrieving the list. The design of SWM primarily covers retrieving raw knowledge, not performing numeric
calculations, but we can envisage adding minor computed queries.
C. Contradiction Resolution Loop (Continuous Maintenance)
This flow highlights how the system behaves when contradictions are detected and resolved, possibly as a
continuous background process.
Most contradiction resolution happens at insertion time (as described in ingestion flow). However, consider
a scenario: two pieces of contradictory knowledge entered the system separately (perhaps one fact was
18
Disk usage: The persistent store’s size grows with knowledge. We will have to either allocate
sufficient disk or implement archiving for old data. Since it's knowledge, probably we keep it all
(unless purging outdated facts). We can compress data on disk (like using binary formats or
compression for logs).
Reliability & Failover: The system should be robust against failures:
If the embedding model is an external service and it goes down, SWM should continue accepting
inputs perhaps by queuing them or storing them unprocessed. The specification includes fallback as
mentioned: e.g., if model unavailable, mark the input and skip semantic vector (store just symbolic).
Later a reprocessing can fill the vector in. This keeps the pipeline from halting completely due to one
component outage.
If the main memory store database crashes, a hot standby or quick restart is essential. The
orchestrator could detect DB failure (through exceptions) and switch to a backup database if
configured. Or run in a degraded mode (read-only memory if possible, or minimal cache) until the
DB is back. Failover logic should be clearly defined: typically, use DB replication and automatic
failover if possible.
Network partitions (if components are distributed) should be handled by timeouts and retries in
communications. We ensure that any message or RPC between subsystems has a clear timeout, and
error paths as described earlier.
Monitoring: The system should be instrumented with logs and possibly metrics (like number of facts,
conflict count, memory usage). This helps detect anomalies (like if conflict count spikes indicating a
flood of inconsistent data).
Maintainability & Testability: Operational constraints also include ease of updates and testing:
Each subsystem can be tested with mock inputs as discussed. For integration, a staging environment
can run the whole pipeline with known inputs to verify outputs match expectations.
Configurability: thresholds like what constitutes high entropy, or which resolution strategy to
prioritize, should be configurable so they can be tuned without code changes. This might be via a
config file loaded at startup or an admin API.
The design avoids hard-coding domain-specific logic as much as possible (except where needed like
"brother implies male sibling"). Ideally, domain knowledge is in a config/ontology, so the system can
be adapted to different domains by adjusting that data, not the code. This is an operational need if
SWM is to be reused across projects.
When scaling up or modifying parts (like swapping the vector database), having modules clearly
separated and interfaced means we can do so with minimal impact. E.g., if a new embedding
technique arises, we replace the Semantic Modeler’s internals but keep its interface same.
Latency considerations: For real-time usage (e.g., in a dialogue, the user might expect a response
within a second), SWM’s operations should ideally be a fraction of that. If any step tends to be slow
(like a large vector search), we might approximate or pre-compute. For instance, maintain direct
mappings for common queries rather than always searching.
Operational Limits & Alerts: We will define certain limits, such as:
Max size of an input fact (to prevent extremely long sentences or huge data from overwhelming the
modeler).
Max number of conflicts it will try to resolve in one go (to avoid infinite loops or thrashing if
contradictory info keeps coming).
If such limits hit, system either rejects input or processes partially and logs a warning.
Alerting can be set up: e.g., if memory usage crosses 80%, send an alert to scale the system or
cleanup; if many unresolved conflicts accumulate, alert to investigate data quality.
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
22
Validation of Input: To prevent injection attacks or malformed data:
The Semantic Modeler/NLP should handle odd inputs robustly. For example, if someone deliberately
inputs a very complex or malicious string (perhaps trying to exploit a vulnerability in an NLP library),
we should have limits on length, allowed characters, etc., and ideally sandbox the modeler if using
third-party models.
The system should reject or sanitize any input that doesn’t conform to expected format. If using
JSON input, use schema validation to ensure no extra fields or wrong types are passed.
This is akin to how web apps sanitize input to avoid SQL injection – in our case, maybe an input could
be crafted to confuse the parser. Good practice is to handle exceptions and not let such input cause
undefined behavior.
Audit and Logging: Security includes accountability:
Every change to the memory can be logged with who made it and when. This audit trail can be
crucial for investigating any unauthorized or unintended changes. For example, log "User X added
fact Y at time Z" or "System auto-resolved conflict between A and B at time T".
Query access can also be logged if needed (to see if someone accessed sensitive info).
If integrated with an identity system, logs might use user IDs. In an agent context, maybe it’s all the
agent itself, but could log which module triggered it or from which source.
Logs should be protected as well, because they might contain sensitive info about the data or usage
patterns.
Handling of Conflicts and False Data: From a security perspective, conflict resolution can be a point
of attack: e.g., an attacker might feed false information in hopes the system overrides a true fact
(especially if it knows the rules like "newer info wins"). Mitigations:
Source credibility is a defense – if the false info comes from an untrusted source, the resolver will
likely not let it override a trusted fact.
Rate limiting and anomaly detection: If a flood of contradictory inputs comes, the system might
detect this as unusual and stop processing them, alerting an admin.
Possibly requiring manual confirmation for critical facts if they are to be changed (like, the system
might be configured that facts tagged "core/critical" cannot be automatically overridden without a
higher trust level input or manual review).
Denial of Service (DoS) Prevention: As an API, SWM should guard against misuse that could
degrade service:
Rate limiting as mentioned, to ensure no one client can hog resources.
Expensive operations like heavy queries might need safeguards. E.g., a query that tries to retrieve an
extremely large chunk of memory could strain the system. We might enforce paging on queries and
not allow arbitrary dumps unless admin (to avoid both DoS and data exfiltration).
The system itself should be robust under high load (tested under stress).
If the SWM is public or external-facing, deploy behind common protections (WAF for APIs, etc.).
Secure Failure Modes: Ensure that on failures, the system doesn’t accidentally expose data or
accept wrong data:
For example, if the contradiction detector fails open (does nothing), a bad input might slip in. We
prefer it fails closed (blocks new info if it cannot verify consistency).
If the system is shutting down or rebooting, it should not accept requests, to avoid half-completed
operations. Use proper shutdown sequences (drain in-flight tasks, commit all in-memory changes,
then stop).
Third-Party Components: Evaluate security of any external frameworks:
The language model used for embeddings should be from a reputable source to avoid any malicious
behavior (mostly not an issue, but we consider supply chain).
The database must be configured securely (no default passwords, not accessible to the world, etc.).
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
•
24
Regular updates and patches should be applied to all these dependencies to fix security
vulnerabilities.
Privacy Considerations: If SWM stores personal data, compliance with privacy regulations (GDPR,
etc.) might be in scope:
Ability to delete an entity and all related data (for a right-to-forget request) – our memory design as
a graph allows that (remove node and all edges).
Avoid storing unnecessary personal info. Only store what's needed for the AI’s functioning.
Possibly implement data retention policies (e.g., automatically purge data older than X if not needed,
or anonymize it).
Test Security Aspects: Conduct security testing:
Penetration testing on the API (try common attacks).
Fuzz testing on input (feed random data to modeler or API to see if anything breaks in an unsafe
way).
Ensure an unauthorized action is indeed denied (test with a token without rights).
Simulate an attack where conflicting info is spammed and see if system holds up.
By addressing the above considerations, Kimera SWM is designed not only for functionality but also for safe
deployment in environments where data integrity and confidentiality are paramount. Security is treated as
an integral part of the system’s architecture rather than an afterthought, ensuring that the semantic
working memory can be trusted as a secure component of the larger AI framework.
Sources:
Knowledge Representation: A graph-based memory structure is used for semantic memory,
representing facts as nodes and relationships (edges). This approach aligns with known semantic
network models for storing facts and concepts.
Entropy & Uncertainty: The system uses semantic entropy (uncertainty of meaning) rather than token-
level entropy to judge information novelty and reliability. This technique helps detect when
information is potentially a confabulation or surprising to the current model.
Contradiction Handling: Conflict detection and resolution strategies are informed by literature on
knowledge bases and AI agent memory. For example, newly acquired information is checked against
existing knowledge and may use temporal precedence or source reliability to resolve conflicts. In
vector-based semantic systems, approximate matching can identify contradictions (opposing
assertions) even if not worded identically. Resolution can involve confidence-based arbitration or
seeking context where both facts might hold true, and in learning systems, contradictions serve as
signals to refine the internal model. These approaches ensure memory consistency and were
incorporated into the design of Kimera SWM.
Evaluating LLMs using semantic entropy | Thoughtworks United States
https://www.thoughtworks.com/en-us/insights/blog/generative-ai/Evaluating-LLM-using-semantic-entropy
