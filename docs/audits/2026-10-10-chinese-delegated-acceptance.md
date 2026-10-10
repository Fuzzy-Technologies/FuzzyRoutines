<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Simplified Chinese delegated acceptance — 2.0.0

## Authority and scope

Maintainer Timur Gilmullin explicitly instructed AIna to perform and accept the
Chinese scientific and editorial review in the active release conversation,
replacing the previously required separate human/native-language reviewer for
this release. This is **maintainer-delegated AI acceptance**, not a claim of
human review, native-speaker certification, or independent journal endorsement.
The narrow exception is recorded in [ADR-0011](../adr/0011-multilingual-documentation-pipeline.md).

AIna-Dev accepts the **258 zh-CN units** below for FuzzyRoutines **2.0.0**:
53 pages, 193 public symbol contracts and 12 module overviews. Reviewed content tree: `758141007c84bc1852dce4e3bedca356170c8a94`.
Remote integration base: [`966d98f`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/966d98f69e13256a46ec7b5dd08f3e3d023beadc).
Acceptance recorded at **2026-10-10T08:14:59Z**. Both review roles are performed by the
same explicitly identified AI reviewer; no second independent reviewer is claimed.
This record does not accept Russian, approve package publication, or waive CI.

The review began from `0ae870379730b72332f7ef404ac4623065d8d953` and its final
Chinese corrections were integrated in local commits `5d5d899` and `6307229`;
these are local integration identifiers, not published GitHub commit links.
Publishing through the repository API may create different commit IDs while
preserving the reviewed tree and the per-unit content hashes. Before recording
approval, every reviewed final file was compared with the integration checkout:
154 physical API/module fragments represent 205 units through tested alias
mapping; 53 page translations match the page review's final translation hashes.
All canonical hashes were recomputed from the current English source. The
normal locale validator passes and preserves mathematical expressions, executable
examples, API section/field identities and source freshness.

## Review findings and resolutions

The scientific and editorial passes compared Chinese text against the English
contract. They checked parameter domains, returns, exceptions, term selection,
exact versus sampled evidence, support/core distinctions, quadrature limits and
historical compatibility. The review retained the historical Universal Fuzzy
Scale names, coefficients and tie behavior. Membership grades are not described
as probabilities. No mathematical algorithm, code example or formula was changed.

Representative corrections and continuing terminology guidance:

| Before / ambiguous wording | Accepted wording / recommendation | Reason                                                        |
| -------------------------- | --------------------------------- | ------------------------------------------------------------- |
| 弱隶属度阈值                     | 弱截集的隶属度阈值                         | Weak qualifies the cut, not the membership grade.             |
| 面积中心值                      | 隶属函数曲线下方面积的质心坐标                   | Identify the centroid coordinate returned by defuzzification. |
| 函数必须对所选积分策略足够规则            | 函数必须满足所选积分策略要求的正则性                | Mathematical regularity is distinct from following rules.     |
| 可变参数标量组合                   | 不定参数标量组合                          | Variadic arity is distinct from mutable state.                |
| 消费者影响                      | 对调用方影响                            | Library consumers are callers.                                |
| 折叠应用                       | 从左向右依次应用                          | Make the left-fold evaluation order explicit.                 |
| 准确参数集合                     | 完整参数集合，不得缺少或增加参数                  | Exact parameter keys are distinct from numerical precision.   |
| Terms and linguistic terms | Use 术语 and 语言术语 consistently.     | Keep terminology aligned across narrative and API pages.      |

All 40 page replacement records and the API corrections were reviewed before
hash binding. No unresolved scientific or editorial blocker was identified in
this scoped AI review. This does not establish formal mathematical proof or
native-speaker certification.

## Primary Chinese journal terminology references

These sources support terminology checks, not the correctness of the library's
implementation or a claim that its scalar API implements their advanced models.
The review records retrieval limits rather than inventing full-text verification.

1. [区间二型模糊集和模糊系统: 综述与展望 — 自动化学报](https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c200133?viewType=HTML),
   DOI `10.16383/j.aas.c200133`: 论域, 隶属函数, 隶属度 and centroid terminology;
   the official HTML bibliography, abstract and Figure 4 caption were checked.
   The caption explicitly uses 质心; complete full-text extraction is not claimed.
2. [多粒度犹豫模糊语言信息融合方法及其在群决策中的应用 — 系统科学与数学](https://sysmath.cjoe.ac.cn/jweb_xtkxysx/CN/10.12341/jssms21047),
   DOI `10.12341/jssms21047`: 语言术语 usage corroborated by the indexed
   abstract. The final direct publisher fetch failed; full-text access is not claimed.
3. [基于多粒度犹豫模糊语言术语集的TOPSIS决策方法研究 — 智能系统学报](https://html.rhhz.net/tis/html/202306015.htm),
   DOI `10.11992/tis.202306015`: the publisher-hosted full article opened
   successfully. Its abstract and introductory definitions were checked for
   语言术语 and 隶属度. The earlier alternate landing-page timeout was resolved.

## Acceptance checks

- Current locale validation: PASS for all protected-content, source freshness,
  reviewer-role, UTC timestamp and source/translation hash checks.
- Negative probes: independently changing a reviewed source hash or reviewed
  translation hash marks the affected Chinese unit stale and fails validation.
- Full `--require-approved` validation remains blocked by the 258 Russian drafts;
  there are no Chinese diagnostics. Russian manifest sections are byte-identical.
- Focused locale-validator and multilingual-architecture tests: **18 passed in
  1.15 seconds** under Python 3.12.14, using `/tmp/fr-review-venv/bin/python`
  with `tests/test_locale_documentation.py` and
  `tests/test_multilingual_documentation_architecture.py`. This checks tooling;
  supported release runtimes Python 3.13/3.14 remain authoritative CI gates.
  No full regression gate was run locally.
- Rendered/browser acceptance and final release CI remain separate evidence;
  these manifest records do not claim that a new browser run has completed.

## Whitespace-only review refresh

At **2026-10-10T09:07:49Z**, AIna-Dev re-reviewed `page:contracts.compatibility` and
`page:mathematics.fuzzy-set-convexity` after deterministic table source alignment.
Every non-delimiter cell is unchanged; only table padding and separator widths
changed. Protected formulas, executable code and API sections are unchanged.
The two Chinese translation hashes and all their role-specific review timestamps
were refreshed after this comparison. Canonical hashes and Russian records are
unchanged. The same maintainer-delegated AI authority applies; no human review
is implied. The audit tables were aligned by the same existing width/padding
convention used by the executable guide index.

## Exact accepted source and translation pairs

Every row is mirrored by role-specific review records in `docs/i18n/units.toml`
with the reviewer above and the initial UTC timestamp, except for the explicitly
recorded formatting refresh below. The source hash uses the existing
`fuzzy-doc-unit-v1` scheme; translation SHA-256 covers normalized UTF-8 text.
Changing either side invalidates approval under the unchanged validator.
The authority is limited to these pairs and the 2.0.0 release, not future edits
or a reusable permission to automatically approve translations.

| Unit                                                                                | Accepted roles          | Canonical source hash                                                     | Chinese translation hash                                                  |
| ----------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `page:api`                                                                          | editorial, mathematical | `sha256:b3b998fc2f2c37662b9bc51d62c14a82ea2a73dd7e3255df06652e0ca3318a5f` | `sha256:78fd5988325b8284310d46e635298efc71aa1c187f9c6ddcc6519d40c13518cf` |
| `page:api.legacy`                                                                   | editorial, technical    | `sha256:bb871cb7cfec01296624328b91169f93716d22f97b05629c92f1116506317e98` | `sha256:8c6354516742f625fd473d57538bcb7faeb2866fbdc944889fd5dd66e5efe7e9` |
| `page:api.modern`                                                                   | editorial, mathematical | `sha256:251a18e081c2afc9a2e4558fd98fb9643674226fb9c2b03b79fb8386bbed2314` | `sha256:eaec21b281831b211c703375fad051cbf330f3bf0ba5624f20d76785969624de` |
| `page:api.modern.alphacuts`                                                         | editorial, mathematical | `sha256:2cb68aa5699f4039c622ddeede294f7e14d9486f42ba38559dd46f43d380c2b0` | `sha256:e77a22c5561c9ac05a6de8780db388bf81e744a570fd60de0f9d1a1b5b959874` |
| `page:api.modern.defuzzification`                                                   | editorial, mathematical | `sha256:df7da6cbba26f7fa4e1ed86b84b42217d16e68015beabd5eef097c14be99ad8e` | `sha256:212c80e00ec2c48ecb62acf60dfb76662121f43fa147244560a636c08d5a7be0` |
| `page:api.modern.domain`                                                            | editorial, mathematical | `sha256:2fe934b8af992e18b81ca54ea9f5e741c156eb1289d41014f53c2a7b04ba5968` | `sha256:1073d72c02d6719467d702063295c7f5004fb18b2265a7a7d288e891aeae0466` |
| `page:api.modern.exceptions`                                                        | editorial, technical    | `sha256:4913d9b698670a7739534770f2c438716deed7172ec699228fbea115573ed6ba` | `sha256:917a20df77b84d7fd07c7fd4a5fce1fd171a4167a1b7815fd90dd2833be18daf` |
| `page:api.modern.fuzzysets`                                                         | editorial, mathematical | `sha256:d2a592c8d08f50c097ec36d3f2ca83229009120ed815903974d4af8bab67fb8a` | `sha256:d45275e2c6327a72e96ef8c0fad6b1eb26ebaa7579b1abb5b5d998cfce6df183` |
| `page:api.modern.linguistic`                                                        | editorial, mathematical | `sha256:844dbd1ec2507923fc335c77f6640e0b84301d09cf1914ca5a1f3742e6959d0d` | `sha256:687685c217c5ae592d404ba70fe76e8947f7dc0b0b2875efc36da028600d3962` |
| `page:api.modern.membership`                                                        | editorial, mathematical | `sha256:18cc21bfd72f3413c0ac3f7110d8cdaf77171b0bac103428a6edf68319e185d6` | `sha256:628b5c4e897358fdeea964f95bc37f250f65f9467690e650f1ebf62cdc53edcb` |
| `page:api.modern.operators`                                                         | editorial, mathematical | `sha256:4c13fb13de5a23fcd35c6ed362ca9c2d981e0e092814a50e76d0446cd1aee668` | `sha256:c95ad2917523bffde88d2679152955613027b13358b82adea92921ca333d6aa3` |
| `page:api.modern.package`                                                           | editorial, mathematical | `sha256:98a42272bb36fe28decc48e9043bcbec4897c2e08c600df145840ce42514692b` | `sha256:2092c142a2acf507f7d02720a93c16d3981cc173c601f86bc08fdae03fb5ffe1` |
| `page:api.modern.properties`                                                        | editorial, mathematical | `sha256:c79eaa220ea775ba9760766990702fac77ed1483a182566522a2ecc7dbe7f2d2` | `sha256:bf89b97236905cec2c8a9442df84fc8e5184a970c0099a1b01fbdfa69b63afb7` |
| `page:api.modern.relations`                                                         | editorial, mathematical | `sha256:d2b141405bca88377c5f5651d86a4afcda7d320c3d6161a1903dd3aa48f010c1` | `sha256:e122d7ec36ede40f723cb2c4abd22a1933253807fc3ef6739da1cba374ac763e` |
| `page:index`                                                                        | editorial               | `sha256:ccc32a7ae0473b42e902d668f55f7268c18642568cefe7f9e50c812971c7dac4` | `sha256:2ddbe29cef4ca314384187b1021464faf26c6b3068d94fe7a09d6cd675ff48c5` |
| `symbol:fuzzyroutines.AlphaCut`                                                     | editorial, mathematical | `sha256:ecb6a322ab9edc837630632dbcb0f1113dc7f58262c4a66ec48d3e59cd8d3c41` | `sha256:06609f1586bea49f6f2ee18a36e4814203697e159975736367c1f5d3461277db` |
| `symbol:fuzzyroutines.Centroid`                                                     | editorial, mathematical | `sha256:059f919e074705641266ddffb6bce5bc8bc094b12efc04648d2b85ca13fbeed9` | `sha256:5d66a875a1c1150a07c579c2b4ec041c764dd56b7b8b60caea81de75adb4a0e2` |
| `symbol:fuzzyroutines.CentroidConvergenceError`                                     | editorial, mathematical | `sha256:0a09150d3e614174b69041b9f0724701c989c1db13d6947b0bdd82f9bb079ed5` | `sha256:4ff8a28d3fcf6f3a82c51d100dc67978261d971e2a73c2adbe35bdb7c7c6e8f7` |
| `symbol:fuzzyroutines.CentroidPolicy`                                               | editorial, mathematical | `sha256:0fcba50f0cc456a6292422ab137b1f57e913b531a0fa5d346c55464094df9458` | `sha256:7b8b87593dcc9e6cda0aeb374ae31d72559dd3a20cd9fc239e60e0ee5c00e18a` |
| `symbol:fuzzyroutines.ComparisonDomain`                                             | editorial, mathematical | `sha256:56d57e410fd1c3b88ca8c43df1143a8fd6974d2cb12e62800569fdc6643ffe0e` | `sha256:3a3ae494c3c56ec421eb53749420455171fcd924f86bfbd6b8888703ecffa1ec` |
| `symbol:fuzzyroutines.ComparisonPolicy`                                             | editorial, mathematical | `sha256:4289b6b905e4a0af9826aee94a7492f76c1b7bc07a264e58b164a6267fe5ccda` | `sha256:517b3641bfe4c235ef053b3245582d717343fb884efc7eb91c22009b375e3cb9` |
| `symbol:fuzzyroutines.Complement`                                                   | editorial, mathematical | `sha256:231cda0cf9d1cd0ae5c6252e344b892d60e5a3304fd4fd4e5aba20b5f170420c` | `sha256:a94e25f2128a8a0cc4dcb3c5cdb3b4ea2cc8ce3856af35b1f4193cfc6b2102e9` |
| `symbol:fuzzyroutines.ContinuousFuzzyProperties`                                    | editorial, mathematical | `sha256:c05ee0b170a3ddf232e462c4dd1e313ac6a6c830c94861547ca8e06499cf95b6` | `sha256:e98f0a8295f687a42493a20e3aeadce018949eeadffe740d81a5522574c89e1a` |
| `symbol:fuzzyroutines.ContinuousInterval`                                           | editorial, mathematical | `sha256:f52028e7bb38995dff4cc850131ff94bc69ffef66f46540f11557bac934b54e3` | `sha256:810f1fd5e0fc49a3f138b2441fbc06264e38de90ff140f005576d0adfb0eb93d` |
| `symbol:fuzzyroutines.ContinuousRegion`                                             | editorial, mathematical | `sha256:b11e4cc978016fd7c845d4d3820ac58f786ed15f2e7ea9b329e3d15123cbed8d` | `sha256:9c4ad916a58773924ee72a729c62c51f63bf506349e107dc9ac8bc3a6c8eee79` |
| `symbol:fuzzyroutines.ContinuousUniverse`                                           | editorial, mathematical | `sha256:6a877df1b307d65d0d604b11c954fbc5e44b228d9a80d0776a70c14151fe6dfc` | `sha256:916bcad7da6c5024c46ae6515ff633d03d34caa10168b6d1093d76d76ee5aab7` |
| `symbol:fuzzyroutines.DeriveProperties`                                             | editorial, mathematical | `sha256:046243351f29d9e4c48bc414ed52a711e3900e0c7819341d227d0c9cc629311c` | `sha256:0e3a50e583f94256322540070ad9ab586965e3f87f3e8863b3ef1ca463016659` |
| `symbol:fuzzyroutines.Difference`                                                   | editorial, mathematical | `sha256:391d1f8f095b1e891962131f48b6018b5f742c98497c720552376a1d12453b61` | `sha256:69a18af88cc279526f7fa1212af8184daad218ddc35d9a8a59e54fc2d528bc95` |
| `symbol:fuzzyroutines.DiscreteFuzzyProperties`                                      | editorial, mathematical | `sha256:0e5bae026a083a589caa0d5a39fd59869cd5155a247249284da190ba4ea7b322` | `sha256:9ba65013c02256a282327e21fbb1a826e6558d4fb56ef053a4514f6d845f1e8c` |
| `symbol:fuzzyroutines.DiscreteRegion`                                               | editorial, mathematical | `sha256:d7c4ffc796b5fbc24341f3c2e3edf9dd8631032ec2294e5918891ff5dbf794f9` | `sha256:d1ff0b5865bd48bdf5b2e815128dea6bf21ac0cb4e3e58d4e53850a1fcb37b2a` |
| `symbol:fuzzyroutines.DiscreteUniverse`                                             | editorial, mathematical | `sha256:ce0c8f40a65d10d363d951f42ae3d023d15a3f47bc4d6ab385611f71527ca891` | `sha256:04486dadaf62cb68b08f1b6f190bed7e00863286f5f0ab781ecca86473810431` |
| `symbol:fuzzyroutines.EqualOnDomain`                                                | editorial, mathematical | `sha256:923325d9ecdbc83f6997095f01dfd15a402e98e6e8d957f5f65345416affa5b8` | `sha256:2abd64ad86ac4ad2927c0afd40ce6bac43710479d8d1a5ac5de5c4ff875f5a89` |
| `symbol:fuzzyroutines.FuzzificationPolicy`                                          | editorial, mathematical | `sha256:59780df0bf471db7949f780f5e1191f5c7435d654307bdb325ce5b4d3c422c09` | `sha256:70bb6dc949fa13c58c0488bc69b1f3c86b5a9a1cb21b4b7222b771d2030a904c` |
| `symbol:fuzzyroutines.FuzzificationResult`                                          | editorial, mathematical | `sha256:40d74a854ff0226b176ff17d2773096eda9748c68859b5c8a61351f71a1a6baa` | `sha256:5cb5d9db3d2751a6f2dbba49acb3f699dac4acf895ff3a8cc0e3baf93d297d26` |
| `symbol:fuzzyroutines.FuzzyRoutines.DiapasonParser`                                 | editorial, mathematical | `sha256:d623403639581adac57487435c5ffaf4a3cbe5a6b61b73dd0984f2a27d67b582` | `sha256:8216a46f6ab04c7305cc261ae1014ef243daee2acc56c329dc4f687776537f3f` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzyAND`                                       | editorial, mathematical | `sha256:11aefd38bd0cdef3b291f22c0219e77df3e343893eb5f347986ba2933147d44e` | `sha256:8c7bb47b71286b0d762c8391778119bd43c4e8a1238dad8f329fce4037b55a12` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzyNOT`                                       | editorial, mathematical | `sha256:a08799c73b2b54cb5fd38f32d383bb90dce97ab4840b9071d463099e5ccb76e0` | `sha256:fb0c748cf7bde6a0a4583e06bbc75c2f53da7fa8faddd94951a6d1b74332a46a` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzyNOTParabolic`                              | editorial, mathematical | `sha256:583ee9648c1ceff8da74785d8ef67ab1c71b947d820fcdc8747f3df27ee21c67` | `sha256:3fa26745fa55e68b4bf5f9f7dc9e13c46bc5905080abae743515ceabcc0505a0` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzyOR`                                        | editorial, mathematical | `sha256:98ca659b2be20af7b2b7964c0f6779222fd51e5e894e475e4a66f1028d477036` | `sha256:a0f0dd10d2620b0f815e08abcff838cdc4dfbbb55fb1fc53305b048d4470ac6f` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzyScale`                                     | editorial, mathematical | `sha256:f615bf8409edfae81e814b4be6a7ac0dbb6a8654a8ab41a760728d3494f379d3` | `sha256:23591da88086149383f39155afe11a0d358c0c39e7ebff57271b3bcdfa2d1e7d` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzyScale.Fuzzy`                               | editorial, mathematical | `sha256:40cd53e749dd85638db8b0e35f48972bf7b3b7b9a15b5656df01174a8c6bc276` | `sha256:3ee96c4e5ab131840ec5785d6b150ae87eb2e588de10d730ef9bfc99e9ab787d` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzyScale.GetLevelByName`                      | editorial, mathematical | `sha256:be2594e4c6775a98fcbc33a1390780b021c4660dd896ca1e58896b979f7d0c08` | `sha256:366f0a338c84c27fee4ba3c3c7507a4f59f6f6316323844799b6bc11905039dc` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzyScale.levels`                              | editorial, mathematical | `sha256:7429fbb46b2cdf8df14775d7667f1ee98082f2aedcedfefca7ca8cffc86e925b` | `sha256:632d97eed72cecb9474a55b35f8e9a292d28b5151b3961bf75ab84c6ff980dfe` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzyScale.name`                                | editorial, mathematical | `sha256:0dd5b36146905f65b4b4a3f4b90ca464f4b9ac66c32949a8a2bd26d15c06e72d` | `sha256:ef89717f41ebd9f4d3cd10054c96dc44a5b3431722c7fcdc55614eb2ca82a200` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzySet`                                       | editorial, mathematical | `sha256:ed4ba1ed35eb3912a13d90c4cc539bea28e512d32486f04fe6213a784f8681f2` | `sha256:fd5cc06fb1801c68e3b6ca0f8212d3c8763ce0b32ca48d3ad074436c12dd2f4a` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzySet.Defuz`                                 | editorial, mathematical | `sha256:92db8d812a36907e50e83244d1e15c9f80c7ec79078a28b1d0811472b82f0c10` | `sha256:5df21d4eeda70507fa2ecbf9b4c5439e4e0c982fe5cfc9c99153dc5feb5fb218` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzySet.defuzValue`                            | editorial, mathematical | `sha256:83c4c4219f897ff4c28aa88758534d131b6ad6f083008cd0627bf25484f34bb1` | `sha256:72b1788222acdb1982893f03040f9b0c3b3b280e2508b53fe4d619721a3e8d6d` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzySet.mFunction`                             | editorial, mathematical | `sha256:fb5f1bb5794dae5f396758e09df910540ddec604e6cbf56d9fff1c7bba81df2b` | `sha256:b6e5e38b459fb03f1199c7a286d6577bde41dd7640094c7aa5e8ef4e7d1b16ad` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzySet.name`                                  | editorial, mathematical | `sha256:daf496678d8077e2ea2e70a35b65519a7b781b493324f9019ee38e024939620f` | `sha256:97702ce8da7a61e30b95982461af3b0786f37686e1d04ce0fe1635c85194199b` |
| `symbol:fuzzyroutines.FuzzyRoutines.FuzzySet.supportSet`                            | editorial, mathematical | `sha256:7f73e60efcb4f9327a392da8aa40be307a8e404261f7eafdc6feff4e68a771e7` | `sha256:8a79251e3e8071aba25ff537371aa50ccf9f14b7e37617975dccd843e6b76bd0` |
| `symbol:fuzzyroutines.FuzzyRoutines.IsCorrectFuzzyNumberValue`                      | editorial, mathematical | `sha256:628318190b48201cda8b2cade6eb076024c9abc66a2aee6d27056389c8188399` | `sha256:4c95e632eb0c4c66d8020ef8061aaf78b91b41914adcf80f255f0b45caac60d7` |
| `symbol:fuzzyroutines.FuzzyRoutines.IsNumber`                                       | editorial, mathematical | `sha256:d999f7ddaaeac83100028206835fba8051bc7cd76bce10af29f6b89413d2d6af` | `sha256:821032469811bafddbb8b4c72bf352791567e64c1b329e7b7510b0aedf930e66` |
| `symbol:fuzzyroutines.FuzzyRoutines.MFunction`                                      | editorial, mathematical | `sha256:23232357e23c0e5b7e89ef4796564c0a9d359f674ea084d07ddb78f01b4e112f` | `sha256:0ac6ad728f1d78df3064406d22aaa4d4c54145e8d01169a8814f3a2378dbd394` |
| `symbol:fuzzyroutines.FuzzyRoutines.MFunction.Bell`                                 | editorial, mathematical | `sha256:a1c9d8eca710faec3e7cd60a14ad5b5350eb214abfe202e6c2f48cc0d5e5ed55` | `sha256:732475769ae133742a992bf4e0701a950d83fdc26b0560513737ca9cd09707f7` |
| `symbol:fuzzyroutines.FuzzyRoutines.MFunction.Desirability`                         | editorial, mathematical | `sha256:5b7054a461770ecfd12e310d988f08320cacb5d00a8909aecdb598d7bb374854` | `sha256:bb37f38cdcd2aa53d372eeb99c4e11d1d60352408a4c0f04765c5be20d406c4d` |
| `symbol:fuzzyroutines.FuzzyRoutines.MFunction.Exponential`                          | editorial, mathematical | `sha256:0b2d17d0db0145c93ffbc500ffed6d9d7bf62758a2fd764210793e9b40465db0` | `sha256:a5167a2e6179322819c22b6735a7503b709c308320d07f52184a8aabf66a3c4b` |
| `symbol:fuzzyroutines.FuzzyRoutines.MFunction.Hyperbolic`                           | editorial, mathematical | `sha256:586482e2cf28c9423f9e1781aa058ce1f19275d085736b9478c15ad9b1f01bde` | `sha256:b0b22f86e79b883b119a5d240d61948597632940178253381e9886a3d6ddee9a` |
| `symbol:fuzzyroutines.FuzzyRoutines.MFunction.Parabolic`                            | editorial, mathematical | `sha256:666c23a8193dae02e3078585c00698e81e42ac5ba34b71ec25b3733f101f6f13` | `sha256:1821986e6cdd4dba5321c64514478bb657ce3cc7977f04941c5771eae21a8673` |
| `symbol:fuzzyroutines.FuzzyRoutines.MFunction.Sigmoidal`                            | editorial, mathematical | `sha256:4e5df78b0c14490121918c2047c26206c592caa957577ac525a6d4dde118c901` | `sha256:b7089738948ffa7e11e42d93834a5426e394d11884cd8e5547627c61ecfc3db9` |
| `symbol:fuzzyroutines.FuzzyRoutines.MFunction.Trapezium`                            | editorial, mathematical | `sha256:8c696636bc2a3d86f7660af9dc0991d18cad05ed952944d6224cb44769c7a1c6` | `sha256:152f90bc958cec9fcee2013fd76b997a9fcf688673ee375533fa3b0fa978ed7f` |
| `symbol:fuzzyroutines.FuzzyRoutines.MFunction.Triangle`                             | editorial, mathematical | `sha256:d68a49c8ba7a4f5b0e8f4d2ad9e100a44b1c954f2d7e630e8e2aa3e4f3f0c191` | `sha256:7fa9577ee14b038becbdc814742cb4cfdda64c4c44169f7aed986a10a0f8cbb1` |
| `symbol:fuzzyroutines.FuzzyRoutines.MFunction.name`                                 | editorial, mathematical | `sha256:124b74989182e657a3012c6209cdc1fad280a994752a6c2633f2f41f55d8579d` | `sha256:1a1f26be0ca405138042c741562f1842948ed6bc7339c64b5ed4e7a113d91961` |
| `symbol:fuzzyroutines.FuzzyRoutines.MFunction.parameters`                           | editorial, mathematical | `sha256:a442a45c5d954720ab76763ba7393b7cceace4cf777e4c674cde251a6278a7b4` | `sha256:54b574cfb9c48829fb52140d765e8207a696c7c6e29fbdc52adf8ee10260eb09` |
| `symbol:fuzzyroutines.FuzzyRoutines.SCoNorm`                                        | editorial, mathematical | `sha256:ed90501fd7144b4d00c0601e0fe2707ece17afe0bd05bd1543ca3b4b0ec4e462` | `sha256:469986cd09f4f7cbeacdcbe47c88fb52c06925b73f9d8b27d97f201dda7dd6b9` |
| `symbol:fuzzyroutines.FuzzyRoutines.SCoNormCompose`                                 | editorial, mathematical | `sha256:a572fa9e51de603dd0f94c5ca39f543f7090bda3be1ad1d4093d7c0a1a10188a` | `sha256:5f389db0b3ba0328157f8556702b9a43034ef51fc1f1c55e98b3c8880c5260f9` |
| `symbol:fuzzyroutines.FuzzyRoutines.TNorm`                                          | editorial, mathematical | `sha256:7760b339c7be1fbb83d852349bb581907821aa86193e302b87a19494e2ec80ff` | `sha256:97ab10e1ac8d3007532405b73b8044fc75bae8ffde671ade0c78ce4369039dcb` |
| `symbol:fuzzyroutines.FuzzyRoutines.TNormCompose`                                   | editorial, mathematical | `sha256:dd32e97be9820abd2c449071984d0a97594203a8f381f16b22e1a8f2763e6da0` | `sha256:aaba4fd506b2eaf1efc3cef04c9c35f91eb87bb81f0d8758407e437879741208` |
| `symbol:fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale`                            | editorial, mathematical | `sha256:728ab821120f12df7d472e3bd2b17af295b826c886a39beb0c933b839c13c025` | `sha256:9eed85b6f2f5fffad1ee5016d23c787b10845a2d9d4031f39f339f03ff41a58d` |
| `symbol:fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale.levels`                     | editorial, mathematical | `sha256:b33482f25694a973cbb9f208247aa8c6fc8d871b2aba80197d4e1ff885405a5e` | `sha256:0cf285cdb5d103a963f92654a01b4f66e26eea744daedd86db955c3f8f8c3def` |
| `symbol:fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale.levelsNames`                | editorial, mathematical | `sha256:9232aae176dcec51cd5a1022e307e7ca76afdaff4de7e786bf5afb440ebb2c09` | `sha256:8c7aacf6b6ad3268739e87fed00adeffbbb7093a2bcd91be32c18ba5119fd0eb` |
| `symbol:fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale.levelsNamesUpper`           | editorial, mathematical | `sha256:4f75a924a42314c95599e5521a1cf0f50d0c028048cc2afab9189d04ff2c6a36` | `sha256:fcfbe5c1f201304b39ed77015280f10c820749ac886b2dcd26568adcdea70ee3` |
| `symbol:fuzzyroutines.Height`                                                       | editorial, mathematical | `sha256:dbeaad0c392550f62c3672203f0cdf5a88b4eb6027f4965eeec307c74d5be4fc` | `sha256:cc1f5abdbf348de628da55444e29afaaf50be927ac4d027f28b28d31f1202407` |
| `symbol:fuzzyroutines.IncludedOnDomain`                                             | editorial, mathematical | `sha256:547ccb2b7e3fa545cd483cb53faa934c03f05a3fada2da418a961e7144d52840` | `sha256:a7c9c311a7ad3b783ca6b2a2a2fc9f9b9c7e77cafb59479af5dc847a5b30e3fa` |
| `symbol:fuzzyroutines.IntegrationDomain`                                            | editorial, mathematical | `sha256:d474de660f4917b27ff7e7d5e32b5bec3657628c44b815310cb2fc9efa758cc8` | `sha256:c988cc88e269c5ffd84a1c89580e19d09806c13c86527f36c8295ed83615c26d` |
| `symbol:fuzzyroutines.Intersection`                                                 | editorial, mathematical | `sha256:c74b03e1f6f6a567d5859bc5a4bee7e21e9b7a971bfd22fb90a32b569c54d156` | `sha256:2091094aea87e80bd5f2ffd96393e5a1f37782b9a8bdf1628075ebb314029441` |
| `symbol:fuzzyroutines.IsNormal`                                                     | editorial, mathematical | `sha256:b249f5bec5da405c1b2150991bcb5767cdc2d4aaa316bab813c3be00d800b240` | `sha256:68d33978de5e3167257bcadf596b0d288a253595b26694c5c0e04293f9ba1e0b` |
| `symbol:fuzzyroutines.LinguisticScale`                                              | editorial, mathematical | `sha256:848cdf58c4c0c8ed025fbb7d2cc50392a910e706111ff87e3b44b4917c5e77dc` | `sha256:c087cf92478cd139db058a9f0b93bf3134bc9740674fe8ac56415c43c89685a1` |
| `symbol:fuzzyroutines.LinguisticTerm`                                               | editorial, mathematical | `sha256:883a7a29e09e99e34dfcec2f5621290a56979e9ac4eec44ec651f494d3a06411` | `sha256:fb6020120c9652f8ea58deef037fba9c2d8684c88b1fa520c297569b4db6a30f` |
| `symbol:fuzzyroutines.NegationPolicy`                                               | editorial, mathematical | `sha256:6675a76125e38ddc1e2f1b9685a1785b86ffcfbda4b1170a3457a69291dede3d` | `sha256:2b1b869560e6b5ea42c4b232aa6d46105fa730de2c31c604600fe663b8099594` |
| `symbol:fuzzyroutines.Normalize`                                                    | editorial, mathematical | `sha256:8436767afea75085984d8620d3797ba9e330bd708e8181bbd8ffd8897015de08` | `sha256:56e229d37c74457b60a63aba5ce886d02a7aca81dc8dbf89fb7f5e5c4f41bc85` |
| `symbol:fuzzyroutines.SNormPolicy`                                                  | editorial, mathematical | `sha256:1514276cc2dd52d4fde98ee4b43dc0887adeb780a01d18d66d4280025ab0a697` | `sha256:7a8678a1e780beac6addd6e6377dd9d54c9eb3b04094c9b436c14c9479465bf6` |
| `symbol:fuzzyroutines.SampleAlphaCut`                                               | editorial, mathematical | `sha256:5f86c50347415650648624ae4ba028ba421860388bd01b3d92433735abf62c8b` | `sha256:d94c8c4b7ccd1a8bcebf6cc109d8d66bfb6c32b9b20494fe6b5e78b3131c428e` |
| `symbol:fuzzyroutines.SampleProperties`                                             | editorial, mathematical | `sha256:6a210a04528b9a4ab9cada6a4a81af79476f39d4f3a795a0e08785f9bc02301e` | `sha256:93c22d1596cbcd6349c0181249a7cc2d4373828fe619d579445bf91ce8b1f477` |
| `symbol:fuzzyroutines.SampledAlphaCut`                                              | editorial, mathematical | `sha256:0d3db0498e523ebbaa77ec0d943a029a2e30db60e28d6ae485df099a7311fedf` | `sha256:abe12f1604e73faf23a68042e816096e0dbe53389a6543888af5f6cba1ff6828` |
| `symbol:fuzzyroutines.SampledFuzzyProperties`                                       | editorial, mathematical | `sha256:71dbe70ac7ac4b2ddf433052c207947cd4fc70512360eb02c910d74311e20def` | `sha256:824b05040ad1b3ee4c931d19d1306a4fd3dec39f0538e02ca68e2bf79724a0e4` |
| `symbol:fuzzyroutines.ScalarFuzzySet`                                               | editorial, mathematical | `sha256:1cb94bed10f53245ecf0ab10af44941ca62237c57eac5af0581c94f9af96e238` | `sha256:868f3fa22ba8c4b60b74acc569000afdec4b5a7520ac805d486ff6edd517f04f` |
| `symbol:fuzzyroutines.ScaleDiagnosticPoint`                                         | editorial, mathematical | `sha256:c8376deea2b8fef813168b1b3046044749965796a197d1eabd7a72504899613d` | `sha256:e20d88e7d12e8709ebf443eb803aab7f68220c08091d0f05dd049642f334fa0b` |
| `symbol:fuzzyroutines.ScaleDiagnosticsPolicy`                                       | editorial, mathematical | `sha256:820722943947e72f85bb9c3dd9ff2ed98dcdd6bc7df04000cbce352a23421541` | `sha256:341d9c39fc0d1021cb1ccca574fc1ac0e3d9e9685f03bc4e28b1f29b49a45242` |
| `symbol:fuzzyroutines.ScaleDiagnosticsResult`                                       | editorial, mathematical | `sha256:ac73bb6343df28721ce440e816ddd179de9f7c15d5d77d94f16c5baf97f08dc9` | `sha256:5963466e7b701615444562b705517ad2158d3b09d4683bd457667772933e6b85` |
| `symbol:fuzzyroutines.TNormPolicy`                                                  | editorial, mathematical | `sha256:6d8348b6f7acd0668a9572ccfd8390898bdaa537cce80b447a31b89683f8060e` | `sha256:259bf135b0e070b199db93b90f13e6c9cfddcc62f2f9242b313ef2f4fca2d8db` |
| `symbol:fuzzyroutines.TermMembership`                                               | editorial, mathematical | `sha256:a52c53c30f0ff281af961ae32e25f2c051921b42609451f4980927b4b82e8eec` | `sha256:fcdf07e98f7600a917a7f2c0c4e8abd9f68c8141efb85093a6ed007a33205d22` |
| `symbol:fuzzyroutines.Union`                                                        | editorial, mathematical | `sha256:3bb9102a4291ee2ccb2640eae3391a77dfab12618cb820f8fb0490a97d6f8e0d` | `sha256:8063d1e4ca839d40307cba4a070dd9973a775abb7b0f878c63a39607d754e41d` |
| `symbol:fuzzyroutines.alphacuts.AlphaCut`                                           | editorial, mathematical | `sha256:442721d23b9ec9178663190ae35ca26b2f1fbd58f80e9ad0d38772355703dbab` | `sha256:06609f1586bea49f6f2ee18a36e4814203697e159975736367c1f5d3461277db` |
| `symbol:fuzzyroutines.alphacuts.SampleAlphaCut`                                     | editorial, mathematical | `sha256:b6902b65388bfac5d8cd2894ddf1f8c9c5c68871881de314caf537ab3e63da7a` | `sha256:d94c8c4b7ccd1a8bcebf6cc109d8d66bfb6c32b9b20494fe6b5e78b3131c428e` |
| `symbol:fuzzyroutines.alphacuts.SampledAlphaCut`                                    | editorial, mathematical | `sha256:a4d4da0bb93b02e35f5691576790ea6352eeb62931c48b25b61c9bac70a9646f` | `sha256:abe12f1604e73faf23a68042e816096e0dbe53389a6543888af5f6cba1ff6828` |
| `symbol:fuzzyroutines.alphacuts.SampledAlphaCut.isExact`                            | editorial, mathematical | `sha256:283484298573ecd33f28ffdf5b141dc556a2d8a779be0353e353dd9a1a241743` | `sha256:5c1d798c8921e39fd0c0270559e03378e29f2df33568368d94c8656938462182` |
| `symbol:fuzzyroutines.defuzzification.Centroid`                                     | editorial, mathematical | `sha256:579be84e19590f007dc0f81afc9af270e71fd94a971144220e306ebbb168b0c1` | `sha256:5d66a875a1c1150a07c579c2b4ec041c764dd56b7b8b60caea81de75adb4a0e2` |
| `symbol:fuzzyroutines.defuzzification.CentroidConvergenceError`                     | editorial, mathematical | `sha256:58472f5e4fc2cf869fc00578f1300e757530f2a4c73902162f0ae1e300c49ece` | `sha256:4ff8a28d3fcf6f3a82c51d100dc67978261d971e2a73c2adbe35bdb7c7c6e8f7` |
| `symbol:fuzzyroutines.defuzzification.CentroidPolicy`                               | editorial, mathematical | `sha256:5322d743920c8aceff7a318ddf85967bf1f731abc0976e5d25c608051dfa7d7a` | `sha256:7b8b87593dcc9e6cda0aeb374ae31d72559dd3a20cd9fc239e60e0ee5c00e18a` |
| `symbol:fuzzyroutines.domain.ContinuousUniverse`                                    | editorial, mathematical | `sha256:c1f3840506ae5a8aaebb315f1ad84cc81a677ff638f7a3cd19eaa9f0dda8d01a` | `sha256:916bcad7da6c5024c46ae6515ff633d03d34caa10168b6d1093d76d76ee5aab7` |
| `symbol:fuzzyroutines.domain.ContinuousUniverse.Contains`                           | editorial, mathematical | `sha256:5b9d499544042f156410d4dfe8e2f9899e48f5c7a3ad1d858bc67a6d56a555bc` | `sha256:894cdc1b06edfafbefa2fa1d15dacb9eb4ed1785dda122762f2dbb5cbdaff76e` |
| `symbol:fuzzyroutines.domain.ContinuousUniverse.isBounded`                          | editorial, mathematical | `sha256:bb6fa4c93e1bcae2ae54ab0d7e47f38bb14bd12a97175921a34d3ba3eb96d379` | `sha256:b73ec8ddba957ac9d8a94ddea99811cf3a7fbe0b7b51cf7cc79bc4b14d1635f3` |
| `symbol:fuzzyroutines.domain.DiscreteUniverse`                                      | editorial, mathematical | `sha256:39ef05be933f2b64a219f5060937b7d2e587a2701d726e1bc8e237081c3cd833` | `sha256:04486dadaf62cb68b08f1b6f190bed7e00863286f5f0ab781ecca86473810431` |
| `symbol:fuzzyroutines.domain.DiscreteUniverse.Contains`                             | editorial, mathematical | `sha256:83ce95da3d453b623203298415e693ab9e173b5b2d5064abaf3b6b66f75db751` | `sha256:5d9024e59cd238c80ac35380d051c91bd82fe56d284fd6612839681dadb3b23e` |
| `symbol:fuzzyroutines.domain.IntegrationDomain`                                     | editorial, mathematical | `sha256:f1fb6b0f00e8220d8766d089a77d09aeac17947e7a59602d1c59d55c4fbc657e` | `sha256:c988cc88e269c5ffd84a1c89580e19d09806c13c86527f36c8295ed83615c26d` |
| `symbol:fuzzyroutines.domain.IntegrationDomain.Contains`                            | editorial, mathematical | `sha256:7da7cfd1289d000ecc468ede0b74ad56f7c0a79c5356f466eaa5e90da97b8b36` | `sha256:63676743b9873164235bf6eaf0d13ac7d8415f835f2a345e789704570a968140` |
| `symbol:fuzzyroutines.domain.IntegrationDomain.FromLegacyInterval`                  | editorial, mathematical | `sha256:a7418f6354ea34d1d337df3736635fe6cc46592dcd546660cfbc2a8500f6a23a` | `sha256:6e5081b8032e368f9ab5a31dd7dffe94b8a7ce283772eeb92a23266ae80fb2ef` |
| `symbol:fuzzyroutines.domain.IntegrationDomain.ToLegacyInterval`                    | editorial, mathematical | `sha256:3069e7d4da243ccf456192a58edddb861f096341668ad2568f584a530c61eed0` | `sha256:14f93461f3a7139247b3332e840f4f0ff25f963e21b9563edeea95ca70f324ee` |
| `symbol:fuzzyroutines.domain.IntegrationDomain.ValidateWithin`                      | editorial, mathematical | `sha256:a0b1e4a0ec65df315da2d8d63c5994f7b15aeef38b22ed0a5c60b7c08f753eff` | `sha256:e09edbf312b18c086c92a8db8583369f2b0008de9067c57293aed10cd1fcc00e` |
| `symbol:fuzzyroutines.exceptions.FuzzyRoutinesError`                                | editorial, technical    | `sha256:931262fc14fbc4674531080d18fc93dc45b941beccb95260a46fecd282a62f35` | `sha256:c0f07c1d471318958bcc0c67c092dc4884b47def34677c7e18dd6a1552df1f69` |
| `symbol:fuzzyroutines.exceptions.InvalidDomainError`                                | editorial, technical    | `sha256:ab26e30965783534e55f75e7130b79973bf90c90f80c9409d5ebb7301d6807ab` | `sha256:606eb3b634901c960651a166c04ab2015c950bfd0f1a9b2fef450664a4c3d519` |
| `symbol:fuzzyroutines.exceptions.InvalidParameterError`                             | editorial, technical    | `sha256:68eec67c11116e32d5b8adc98840e204b78bac1417ac19cb2ab011418b891b46` | `sha256:132643dc301244edd76b39e967ab0083558df05e479e0ef1bed5752b008bf4d6` |
| `symbol:fuzzyroutines.exceptions.InvalidParameterTypeError`                         | editorial, technical    | `sha256:f4d59c7129524d6f4fafdf1105d74102103002feb30c91edd2a314c5f336d1a8` | `sha256:341f7260ba36a2afd113ce64fdc75b2a645439b2e5e74872a49eba8ad81d7288` |
| `symbol:fuzzyroutines.exceptions.NumericalError`                                    | editorial, technical    | `sha256:602d0ee237f4cfe7bb701bc7963427bf8f37e3e119ceb988d3317d607020f6e6` | `sha256:961b02d22abc679636065058035c71ca4177bdd1d8fff8cb2e9796867dedf49d` |
| `symbol:fuzzyroutines.exceptions.UndefinedResultError`                              | editorial, technical    | `sha256:4e93e8e7587670b53e44525e518c6f1575c6d1d009dd82ac8be886ed8fcb8e85` | `sha256:6428c011b11e88e01c47f9ff61ca5f46a7b2d1dddd06cd47e1a1b85d797ab02e` |
| `symbol:fuzzyroutines.fuzzysets.Complement`                                         | editorial, mathematical | `sha256:5aac8f5209aafae85580276033e20f92497caa1e55b77d4efcc0609f1623b699` | `sha256:a94e25f2128a8a0cc4dcb3c5cdb3b4ea2cc8ce3856af35b1f4193cfc6b2102e9` |
| `symbol:fuzzyroutines.fuzzysets.Difference`                                         | editorial, mathematical | `sha256:b1f35adb8f0a6624397c5827d40f3ef44423db7d498833997c2f6d7e676e8f95` | `sha256:69a18af88cc279526f7fa1212af8184daad218ddc35d9a8a59e54fc2d528bc95` |
| `symbol:fuzzyroutines.fuzzysets.Height`                                             | editorial, mathematical | `sha256:a88db233677cc89ed1acd5b509f8213a24998bac1d49d8c5cd44678673965823` | `sha256:cc1f5abdbf348de628da55444e29afaaf50be927ac4d027f28b28d31f1202407` |
| `symbol:fuzzyroutines.fuzzysets.Intersection`                                       | editorial, mathematical | `sha256:bde0a50739ff83faecf3d35a12ff358163b5c5576433d0d7f8c45281ad9e3792` | `sha256:2091094aea87e80bd5f2ffd96393e5a1f37782b9a8bdf1628075ebb314029441` |
| `symbol:fuzzyroutines.fuzzysets.IsNormal`                                           | editorial, mathematical | `sha256:acc011cc1be9bc3393ad4223ebd9719bfa094e043be2769fb4da50ddc8e10a10` | `sha256:68d33978de5e3167257bcadf596b0d288a253595b26694c5c0e04293f9ba1e0b` |
| `symbol:fuzzyroutines.fuzzysets.Normalize`                                          | editorial, mathematical | `sha256:8fcb31870fa613efd0e6ebb2c8cab24dce5970b8aade7ecd7f5058ff70747405` | `sha256:56e229d37c74457b60a63aba5ce886d02a7aca81dc8dbf89fb7f5e5c4f41bc85` |
| `symbol:fuzzyroutines.fuzzysets.ScalarFuzzySet`                                     | editorial, mathematical | `sha256:f61c09cdf632a8ac01f2678efea6bd035834de93d4f41ab51ce483dfefa09575` | `sha256:868f3fa22ba8c4b60b74acc569000afdec4b5a7520ac805d486ff6edd517f04f` |
| `symbol:fuzzyroutines.fuzzysets.ScalarFuzzySet.Membership`                          | editorial, mathematical | `sha256:6d51bfd902c91e6680f1be6795ea0dfc842744b8489a575d3c2505d08fa0de7f` | `sha256:ca11ab8de94b76fc61710c1ab638701cb550b27e43e23a1c5ef85fcea67bc430` |
| `symbol:fuzzyroutines.fuzzysets.Union`                                              | editorial, mathematical | `sha256:447e5d47a1c1af1b08b6e39b600c44444875be79be73aeb79c7c6004533253cd` | `sha256:8063d1e4ca839d40307cba4a070dd9973a775abb7b0f878c63a39607d754e41d` |
| `symbol:fuzzyroutines.linguistic.FuzzificationPolicy`                               | editorial, mathematical | `sha256:54c775b80a7a1c8d0653ba3eeb8a5489a08af0f7412ca1f95e8e1147123f57f1` | `sha256:70bb6dc949fa13c58c0488bc69b1f3c86b5a9a1cb21b4b7222b771d2030a904c` |
| `symbol:fuzzyroutines.linguistic.FuzzificationResult`                               | editorial, mathematical | `sha256:3beff07dfc28f8e4f960bf55f2ce265666303ec299a68c6b170b03a8ab0fdbb2` | `sha256:5cb5d9db3d2751a6f2dbba49acb3f699dac4acf895ff3a8cc0e3baf93d297d26` |
| `symbol:fuzzyroutines.linguistic.FuzzificationResult.isMatch`                       | editorial, mathematical | `sha256:245bbb18792f606a0320f88381e62770106e77972d0f0323300040b81e4bad5a` | `sha256:ac5c3f9e41924fe3ff0059bb895b7b0828601946a345e43650503042102023ea` |
| `symbol:fuzzyroutines.linguistic.FuzzificationResult.isTie`                         | editorial, mathematical | `sha256:a6512dee7da4b6f0f814f6ea22ae81a172c2d3f63264c2080b7327280f568651` | `sha256:7bcbf8ac8d0be1a24b790c22635155d1fad20b8d56b0263b35b1d090db733365` |
| `symbol:fuzzyroutines.linguistic.LinguisticScale`                                   | editorial, mathematical | `sha256:7fe5327b5627278bf690538819948769e512cb393b5b0ba34deea5f78192682c` | `sha256:c087cf92478cd139db058a9f0b93bf3134bc9740674fe8ac56415c43c89685a1` |
| `symbol:fuzzyroutines.linguistic.LinguisticScale.Diagnose`                          | editorial, mathematical | `sha256:cffb1731fa865f644867521b3001677c5def75556f14b9504a30c357a301aea1` | `sha256:79f65691604910bb464b875257d3a5cd7dd4ec990d989db13b022ebc1625e5ce` |
| `symbol:fuzzyroutines.linguistic.LinguisticScale.Fuzzify`                           | editorial, mathematical | `sha256:c7755a5772dde0e9f2019575694bc77eb04e89821592927c930ac7d9a6dff64d` | `sha256:54aa62e6704c96c6af1b01aa80efceceed36b2badc3665f8b63c49c0582841b6` |
| `symbol:fuzzyroutines.linguistic.LinguisticScale.GetTermByName`                     | editorial, mathematical | `sha256:6adcb23be8cb154ba5645edc63da9ec07c78ae3c7dd3bbce0e57c89b377efa5e` | `sha256:0ef19d3d103ad6e6616c2d67aced636aadd5aa596b54befbeb0e238cf334c51a` |
| `symbol:fuzzyroutines.linguistic.LinguisticTerm`                                    | editorial, mathematical | `sha256:ee601bce05c76360a791dc980f248ef4ce3ff8c08e5e462a92e31a3f10bdfcb6` | `sha256:fb6020120c9652f8ea58deef037fba9c2d8684c88b1fa520c297569b4db6a30f` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticPoint`                              | editorial, mathematical | `sha256:0b30c010e0b789db768515b7341196689b2166cda6851d212cc195aa4b248d48` | `sha256:e20d88e7d12e8709ebf443eb803aab7f68220c08091d0f05dd049642f334fa0b` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticPoint.activeTerms`                  | editorial, mathematical | `sha256:e51f94d8908a0408716c136261b2e05d8a7b666acc379863b1c2043a31f3ad80` | `sha256:2ad0cfd62349f49dd8ab8e04bf59ea80204cd5323b7f0623002762c1420626e4` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticPoint.isGap`                        | editorial, mathematical | `sha256:7921f3e01a74c99469a99e53ceb6fefcce1a3998c887976a16bf8942d244c97d` | `sha256:c35e0ba08b128817305163b3ee353797e05de52935a83e97294d932a8c4b75db` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticPoint.isOverlap`                    | editorial, mathematical | `sha256:e05a752b1756672e54b9776f99c84b1b1386cd9f4633d070840730ec7a94a8de` | `sha256:65ef8addece6fde6020ca039318bc525fb5596edf8b786d6c1194c8b8d09eb0f` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticPoint.maximumMembership`            | editorial, mathematical | `sha256:d21228007a2a563a3de6767604109a8f845f8340bb6efd81d4613ef7cf010fba` | `sha256:f4405ae6d6093a87fb7ccdc5254ee169f1a5e46cd9cde94e2ec01402cdd263d9` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticPoint.membershipSum`                | editorial, mathematical | `sha256:2b049914f437c12984eade6e60a6d799d1ddfcbfd2eb48841c31657004f72564` | `sha256:431a31ba37e946aa865199fcc692f86031ad02f527beb1a1b5386b3506a6b06b` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticPoint.partitionError`               | editorial, mathematical | `sha256:bfaa941a2ace02e392d5fd305ef6a451dfc237cbfee505c112008283f6199ab1` | `sha256:3fe0fca414a11846c678549aa5db48c8981335da12ed981aa82dd44e85e698c0` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsPolicy`                            | editorial, mathematical | `sha256:f22f08bc819a63300fa75b63d8e3e395dd64873475145278261199bba55c0469` | `sha256:341d9c39fc0d1021cb1ccca574fc1ac0e3d9e9685f03bc4e28b1f29b49a45242` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsResult`                            | editorial, mathematical | `sha256:d6b0ade2434158a538d7f1d62f977839295d51b9215eb68056c8ea82b8e1c89e` | `sha256:5963466e7b701615444562b705517ad2158d3b09d4683bd457667772933e6b85` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsResult.gapFraction`                | editorial, mathematical | `sha256:5e2f2fede7e880cdc91084d702da9fabb0271fd2bf5f0a4e429b7e9919c8a4c3` | `sha256:d3c5843db72862e701017000172448c261099b515a36e4a68945a7324f0c6dee` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsResult.gapPoints`                  | editorial, mathematical | `sha256:0f1f35bdd6923711775161e9e2bab9b352a6ff44059a2217087cef305da4ae5e` | `sha256:5dd7866f78560991764ba2b79b0d9fefc61a5e95d9e6d65f05e0c4b2c3f38043` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsResult.isPartitionWithinTolerance` | editorial, mathematical | `sha256:ad035a30a1a9daf771023c101aae85dbec513b0fcfc06ca4a625d636a8fb02c6` | `sha256:041279de3b790cd1c5bab6923bc91569fed3ef002531808b7a6028c4b87e17ce` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsResult.maximumActiveTermCount`     | editorial, mathematical | `sha256:9c9fa5c1b75bc792ac4e9cfea60a67edc1338758a774937a83e3e68f319391ba` | `sha256:8b76a2681578f85da7c70201194f35c1c8a6e8e576017bee950e280142cfad66` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsResult.maximumCoverage`            | editorial, mathematical | `sha256:aa9c92c6d31afe709478886fcbbfaf37c5fade7ab6cfa2d7ef1c5de917ad167a` | `sha256:f75726c7f58b971c78db00f2045a7c0936137e2113e2536686bf5ead1bc39859` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsResult.maximumPartitionError`      | editorial, mathematical | `sha256:025ff3a539b37b3b25c8d0752969d26d89e35c96d6734dc30829b650c3dec506` | `sha256:cadb75627e749cca8bfd6d4c3f024a9c74cb99bdd47876d6c90d3cc9f40ead8f` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsResult.meanCoverage`               | editorial, mathematical | `sha256:17a2fcdd209de2c8ad011097303a123d3c1ef3663763a02f975e1dc2bf2092a8` | `sha256:3e9e1abbeb84ef54e2701f5bf205a516a2738d953a44318a38fc978dcaec1743` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsResult.meanPartitionError`         | editorial, mathematical | `sha256:41cf64a58b514892a8dbade7529d1c6d09dbf62c360986d46cd645e5ad0a5a09` | `sha256:8290718853ab3451d355dd381adebd9c28d907ebc0fe7bb929c3c63d980fa94f` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsResult.minimumCoverage`            | editorial, mathematical | `sha256:bdd7650170b4bed082c10f5e8eadf9c8af82c007b858fc6c6bcfe4871b2570e0` | `sha256:cbd7c16904f3fee613457cdbf86f3ee70b0b495c812604f8cac04b8b5c539c51` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsResult.overlapFraction`            | editorial, mathematical | `sha256:8a1094a13a4a47cea016f724d02d2866b3ba39aa78799f078e644b3f815cd7a8` | `sha256:a54c1f85f02dc9b79ed837bfb17275e0c2094b9a422e1a654db91dfed4eba9d3` |
| `symbol:fuzzyroutines.linguistic.ScaleDiagnosticsResult.overlapPoints`              | editorial, mathematical | `sha256:0b61a6ae7d29f4efe34787436b674a28f3a40f9272eba13116020959ae92ee7a` | `sha256:aac547b8afe4d1f3098f8d9c757ed4851ddbe34c9df0ce32dd161d73f007042d` |
| `symbol:fuzzyroutines.linguistic.TermMembership`                                    | editorial, mathematical | `sha256:cd402f54d170b3322c1b3ec6689eb4aa7d0c5df0b60e7739fc50d2b63db12ebc` | `sha256:fcdf07e98f7600a917a7f2c0c4e8abd9f68c8141efb85093a6ed007a33205d22` |
| `symbol:fuzzyroutines.membership.Bell`                                              | editorial, mathematical | `sha256:34b5e7e04fd4f7faf46bf1703b32a24be7ee491e24311801c117832bd21a9c95` | `sha256:0ffbc1c5ef2ce879c1190e4d44a74a8a57b2e3092d280083b2e816442c8eadff` |
| `symbol:fuzzyroutines.membership.Gaussian`                                          | editorial, mathematical | `sha256:4173db52e7a90a009889b0e982f8ca330b030bea24782e99ba9e687404f61e37` | `sha256:6767386fb6aad785813e7db1a9915c8659eaa4a31312c79b1fa6eaa654821fcb` |
| `symbol:fuzzyroutines.membership.HarringtonDesirability`                            | editorial, mathematical | `sha256:b88fbdae5d8bd75df64e1f136e591c2cd75e578277ddc18b67c116ce20241ad9` | `sha256:bda7c9dcc5f1f44a43ea02cf2c0b15592fed78d00b43a82c5578d569c9808dd1` |
| `symbol:fuzzyroutines.membership.Hyperbolic`                                        | editorial, mathematical | `sha256:dc4b5157d980391ac0c795f1612425667f5770b7290675543498c02aec29069b` | `sha256:61f3332d2bb4e6a53f3ac5691d6bd248fa6c939a6cf9f8717f173b648af23b6e` |
| `symbol:fuzzyroutines.membership.Logistic`                                          | editorial, mathematical | `sha256:c2eb75ace8e5f11e99b1aac45337d6f3463741910a5fe4e6e07e2029175fa0a3` | `sha256:e6a3b82937b8b5d0576adbf824e9f1aafa1480f7f1af8351a623984fd46f7aa5` |
| `symbol:fuzzyroutines.membership.MembershipFunction`                                | editorial, mathematical | `sha256:29df5354ed777d3fe170e3dbe7cfabba4fd1cbb0dab491cc145db286922ae996` | `sha256:f7fd77d2d7e3def7d5c184822bb2613837a929413fc981d77865e605191b3611` |
| `symbol:fuzzyroutines.membership.MembershipFunction.Evaluate`                       | editorial, mathematical | `sha256:769bc1c27d3d5d476ef11edf2f18b32637487da59dd926a893c2e02a1cf41d9b` | `sha256:604fa96eabe406d5817e6b6ce919085ad078b15521eb7aba74e0733a754df03e` |
| `symbol:fuzzyroutines.membership.MembershipFunction.parameters`                     | editorial, mathematical | `sha256:98b0a34a266200f11012936c85b7be445d014e22ae37b19734592ffa739a91d6` | `sha256:3cf68daa7f315301a63ac1cefa4400cfd3436617e233229a4910a4c7d4288007` |
| `symbol:fuzzyroutines.membership.SShoulder`                                         | editorial, mathematical | `sha256:a4eed302fc6ad3e5e29f4c176e7a027e06baaa61c31b193b0886e14a22208671` | `sha256:9cdff0faef621752d09642c8548cefbe4e1274a6c1b133deb1240c53d5531a77` |
| `symbol:fuzzyroutines.membership.Trapezoid`                                         | editorial, mathematical | `sha256:12f1a317b2879ff6425e7d61efeff55f0e211b0648b97ea6e5ebc9b7505b33d3` | `sha256:124872dccbb26fa3d44cd7c4cbd8105695c31ee5772fa87a0653bfbcb3ec940b` |
| `symbol:fuzzyroutines.membership.Triangle`                                          | editorial, mathematical | `sha256:469a2242f3b73e78128b0b1b81f8caad95008dc47b423900118b518fb4caa68e` | `sha256:da7963aecef62b0491483dbc5de134a1999f3fa42a0a26405591ff9926100638` |
| `symbol:fuzzyroutines.operators.NegationPolicy`                                     | editorial, mathematical | `sha256:c5a736ee688c14b4fd5085d6fb3facc5dae642f3beaa351b6424124d9992e36a` | `sha256:2b1b869560e6b5ea42c4b232aa6d46105fa730de2c31c604600fe663b8099594` |
| `symbol:fuzzyroutines.operators.NegationPolicy.Evaluate`                            | editorial, mathematical | `sha256:ad4f8df13d573de59a93e7bb45a1a3e38197d3aff234cf099d3dd4cda6efdea8` | `sha256:40470f68e6e82e39f060b048ef0ca94c3ac9e6006027164399d687f55ff8a1d1` |
| `symbol:fuzzyroutines.operators.SNormPolicy`                                        | editorial, mathematical | `sha256:4b9d7aa20f27ea44715181edf86f12736ef185eb483b7e1ec53e8e43c9458d6a` | `sha256:7a8678a1e780beac6addd6e6377dd9d54c9eb3b04094c9b436c14c9479465bf6` |
| `symbol:fuzzyroutines.operators.SNormPolicy.Evaluate`                               | editorial, mathematical | `sha256:2a43f6dcdce2d868928d1a8d75a575bcac30c9d17075ca9a53d892f4822b0ad7` | `sha256:04141b5de21b00ab5807841b3cd90321e5f2b78db089e73528bc9df66d5306e0` |
| `symbol:fuzzyroutines.operators.TNormPolicy`                                        | editorial, mathematical | `sha256:a25076b23a756ffe085f5a3c7b7ba16c6f18b91df2531440b5b5cfa3e3224ec4` | `sha256:259bf135b0e070b199db93b90f13e6c9cfddcc62f2f9242b313ef2f4fca2d8db` |
| `symbol:fuzzyroutines.operators.TNormPolicy.Evaluate`                               | editorial, mathematical | `sha256:09ee1b737766dae8409c44830c618c9d3b1ee21e1e2d788e0db840df7f375f8e` | `sha256:398e5a8cc7db05f56f59f199732af02dfb58d9e070d63d928194b73c6c46f646` |
| `symbol:fuzzyroutines.properties.ContinuousFuzzyProperties`                         | editorial, mathematical | `sha256:e6f7796380b7026850d089320f30f190e522486c8cdc8bb4d41006b74ccaf54c` | `sha256:e98f0a8295f687a42493a20e3aeadce018949eeadffe740d81a5522574c89e1a` |
| `symbol:fuzzyroutines.properties.ContinuousFuzzyProperties.isExact`                 | editorial, mathematical | `sha256:fe4ddecec4c4484366f502bfb9b4ec8fd99d63d6923ceb420bedd5b01599d867` | `sha256:25007137fa8e89a749b622c98ac6bf8df1c7e6bee44503576406c6c068339e4d` |
| `symbol:fuzzyroutines.properties.ContinuousInterval`                                | editorial, mathematical | `sha256:c787d59943c739d5864ea60d0fd4fc6dd97ebc766fc5e8babdc645610b1b2355` | `sha256:810f1fd5e0fc49a3f138b2441fbc06264e38de90ff140f005576d0adfb0eb93d` |
| `symbol:fuzzyroutines.properties.ContinuousInterval.Contains`                       | editorial, mathematical | `sha256:08367eb6ac60e993b3d722198d94bc68579fc990c63e5f76f61619494d266210` | `sha256:ea13458d01a2baf56560146224f510434e03da2be512b2ce57f40306f87493cf` |
| `symbol:fuzzyroutines.properties.ContinuousInterval.isSingleton`                    | editorial, mathematical | `sha256:8d60c81c54553f2c1bb967e6a6dcd44e5740b50f8344195ff52e490502eba045` | `sha256:8d2750c049f5803c6284ec9e4a4f7c365e7cd301e3f446543e4a82f82720786c` |
| `symbol:fuzzyroutines.properties.ContinuousRegion`                                  | editorial, mathematical | `sha256:12ffffaf7e23aa2dadbec37542bbf7b272406810ab90fa46b02f45783fec8201` | `sha256:9c4ad916a58773924ee72a729c62c51f63bf506349e107dc9ac8bc3a6c8eee79` |
| `symbol:fuzzyroutines.properties.ContinuousRegion.Contains`                         | editorial, mathematical | `sha256:eb2062c4200c61e2a01ad541fbdcc7812bd430f61f07c8724249b92b9ad23e55` | `sha256:77a46c7d9afb3c34daddf91f3de7fce3c38e301940c32da26704c550603045ec` |
| `symbol:fuzzyroutines.properties.ContinuousRegion.isEmpty`                          | editorial, mathematical | `sha256:da93dc8c9b8b66e42fe1190fb12f7f38108978d531d3a1ddcc983a121af598d4` | `sha256:dd3fbe2ea8c46bf767931bd79a6aab917fdc48e1928dae321f23cd713a7320d2` |
| `symbol:fuzzyroutines.properties.DeriveProperties`                                  | editorial, mathematical | `sha256:c5e405a3daf606673d60247d5f7e92250eed6e99efae90c6cdbe7fe2946fd113` | `sha256:0e3a50e583f94256322540070ad9ab586965e3f87f3e8863b3ef1ca463016659` |
| `symbol:fuzzyroutines.properties.DiscreteFuzzyProperties`                           | editorial, mathematical | `sha256:64b9ef21eda5236bdeb48851f1b8fe4cd83e620c04bac8c4a22b6b0ec28d9a1f` | `sha256:9ba65013c02256a282327e21fbb1a826e6558d4fb56ef053a4514f6d845f1e8c` |
| `symbol:fuzzyroutines.properties.DiscreteFuzzyProperties.isExact`                   | editorial, mathematical | `sha256:be5fc70931e2033f0c2c91e190dac4d3a87fdabcf5c4bf200e72bb24aae457b2` | `sha256:40bf1c484d6ecb22376c3ec7225b3474ebb9232948d425a614329c264ae911a0` |
| `symbol:fuzzyroutines.properties.DiscreteRegion`                                    | editorial, mathematical | `sha256:f0635b27e8505d4bf48ac84d302fb24799435e71a252381e0c13b1f4e69e4c7b` | `sha256:d1ff0b5865bd48bdf5b2e815128dea6bf21ac0cb4e3e58d4e53850a1fcb37b2a` |
| `symbol:fuzzyroutines.properties.DiscreteRegion.Contains`                           | editorial, mathematical | `sha256:7002b174bf7d1bbb10f2ecbb8230283a03370ec91480e170ad1ef50eac6db16f` | `sha256:87d58f3605ed500b7b17f41dbc185bf8462799eadb0e361b0c858e3a24c727ab` |
| `symbol:fuzzyroutines.properties.DiscreteRegion.isEmpty`                            | editorial, mathematical | `sha256:1de97b536020671c8aef604c9d1e75c5342f168365977e84a936ad13d84813a4` | `sha256:4e427b26d681cffa07ef3177d5683c75096a40598c895e7f2602ffec9f85c57d` |
| `symbol:fuzzyroutines.properties.SampleProperties`                                  | editorial, mathematical | `sha256:3f42fbd697db95700cf3ba47c5cb35722f06a7e486534d0bab0bc43d16a9412b` | `sha256:93c22d1596cbcd6349c0181249a7cc2d4373828fe619d579445bf91ce8b1f477` |
| `symbol:fuzzyroutines.properties.SampledFuzzyProperties`                            | editorial, mathematical | `sha256:d1bc144d778bce93772e6ca6b129999a37b3429f0c3ea9428b8d5d1ad72f1c5c` | `sha256:824b05040ad1b3ee4c931d19d1306a4fd3dec39f0538e02ca68e2bf79724a0e4` |
| `symbol:fuzzyroutines.properties.SampledFuzzyProperties.isExact`                    | editorial, mathematical | `sha256:7290464d47af683bf22fcf0ad06d741a10b43c3f08222e67cd9d35fae1d444be` | `sha256:ee0746166290202bfa9b58d7e72d0469835566a3eefb5a8fbbe156f8115ff4cc` |
| `symbol:fuzzyroutines.relations.ComparisonDomain`                                   | editorial, mathematical | `sha256:fa81f3c6b5028deb4ef3c48a41a2a2a39954996dfecfc39cf5d051611ecabe7b` | `sha256:3a3ae494c3c56ec421eb53749420455171fcd924f86bfbd6b8888703ecffa1ec` |
| `symbol:fuzzyroutines.relations.ComparisonDomain.ValidateWithin`                    | editorial, mathematical | `sha256:7402314f08061f31e3bde325fee25bdf888f73dc1fe3748024d7f09916af4f12` | `sha256:c27dc156533288ab3da80e1811a666f4cffc70ec6f86d3cd543353f768709958` |
| `symbol:fuzzyroutines.relations.ComparisonPolicy`                                   | editorial, mathematical | `sha256:d68a56234c1e0f841318e638bfb1b56fd3181ffc4cb437a2cc06df5602ace5e6` | `sha256:517b3641bfe4c235ef053b3245582d717343fb884efc7eb91c22009b375e3cb9` |
| `symbol:fuzzyroutines.relations.ComparisonPolicy.Equal`                             | editorial, mathematical | `sha256:0dc5ecd8a5cf371a98d9dab1fbeff119bc1b21d90eb05d07f604c1809e6ec730` | `sha256:7cb7531f5898602f4f83ae530ae5eecb960ec3d54f1a717f4d2db6616b5b5ca4` |
| `symbol:fuzzyroutines.relations.ComparisonPolicy.Included`                          | editorial, mathematical | `sha256:7d0684f26457c153127a4169823a07ef35eb0bbd5660cafa66fbeea36dd69b1e` | `sha256:ddf78a05e49e4d80b68248a7ecea9305a3c8efc0466ffc7f8028bcc6cbbb6305` |
| `symbol:fuzzyroutines.relations.EqualOnDomain`                                      | editorial, mathematical | `sha256:b8bc2cb7f8a282433fbb2b722de4e6f405a59f48b62a903ff5f0c9d0c10e6378` | `sha256:2abd64ad86ac4ad2927c0afd40ce6bac43710479d8d1a5ac5de5c4ff875f5a89` |
| `symbol:fuzzyroutines.relations.IncludedOnDomain`                                   | editorial, mathematical | `sha256:7ff99109e4afac7419058976f735c68acf58716e0bc278565894448008ef7807` | `sha256:a7c9c311a7ad3b783ca6b2a2a2fc9f9b9c7e77cafb59479af5dc847a5b30e3fa` |
| `symbol:fuzzyroutines.membership.MembershipCallable`                                | editorial, technical    | `sha256:73f1a324a0c31f5430a1e2e707c266b87fde40137eed1fb09865cd2adc567ebf` | `sha256:6cf2d48582eba5cab236030ab12ffe31c973542b18ac2be7109fec820b1b092a` |
| `symbol:fuzzyroutines.Bell`                                                         | editorial, mathematical | `sha256:832edaf9cf8b105c4218049c40b74d9b1ff3e9d8f182523c53820d93dfe89ae0` | `sha256:0ffbc1c5ef2ce879c1190e4d44a74a8a57b2e3092d280083b2e816442c8eadff` |
| `symbol:fuzzyroutines.Gaussian`                                                     | editorial, mathematical | `sha256:282667a1eb27c9787918c3770c9dbe928a4d4fb671a664dbe8c41baf27a109aa` | `sha256:6767386fb6aad785813e7db1a9915c8659eaa4a31312c79b1fa6eaa654821fcb` |
| `symbol:fuzzyroutines.HarringtonDesirability`                                       | editorial, mathematical | `sha256:8f8fc7c263762e55ccdbe5dd6ca9b71cad38c1b705fd32954a152f7080c6daf2` | `sha256:bda7c9dcc5f1f44a43ea02cf2c0b15592fed78d00b43a82c5578d569c9808dd1` |
| `symbol:fuzzyroutines.Hyperbolic`                                                   | editorial, mathematical | `sha256:92d1f0c78f74ac112cc107db171de032b0bfd19878f3debdf03f31b7dc5b8da4` | `sha256:61f3332d2bb4e6a53f3ac5691d6bd248fa6c939a6cf9f8717f173b648af23b6e` |
| `symbol:fuzzyroutines.Logistic`                                                     | editorial, mathematical | `sha256:923f01002c666c3b154ad67cbabbcc605efee2d6b494a1e78b30259c9b651c1e` | `sha256:e6a3b82937b8b5d0576adbf824e9f1aafa1480f7f1af8351a623984fd46f7aa5` |
| `symbol:fuzzyroutines.MembershipCallable`                                           | editorial, mathematical | `sha256:cd36f745573e6139f1293efaea48733801993480f4cdb4fa1762a60a3e3cb305` | `sha256:6cf2d48582eba5cab236030ab12ffe31c973542b18ac2be7109fec820b1b092a` |
| `symbol:fuzzyroutines.MembershipFunction`                                           | editorial, mathematical | `sha256:79ec75626dbc4c452522f7d0db485290dcff8d34dc8e6f224d475fb970632a4b` | `sha256:f7fd77d2d7e3def7d5c184822bb2613837a929413fc981d77865e605191b3611` |
| `symbol:fuzzyroutines.MembershipScalar`                                             | editorial, mathematical | `sha256:6b5ec5792357a433f282bdc88419042b646090628dd10742b65e31cb163d95d8` | `sha256:617eb81a84ce0c8ad50c05075381690062e83c98b3a82ab3443be93fcb4d6c52` |
| `symbol:fuzzyroutines.SShoulder`                                                    | editorial, mathematical | `sha256:5721ca93afb5dd6e3f3473c76156bdea6b5e4e82335e241a72746a5cd46730a4` | `sha256:9cdff0faef621752d09642c8548cefbe4e1274a6c1b133deb1240c53d5531a77` |
| `symbol:fuzzyroutines.Trapezoid`                                                    | editorial, mathematical | `sha256:09a08f7263b2b84038dce520c85c06e0722248b18eccb28ae4376ce065a1877a` | `sha256:124872dccbb26fa3d44cd7c4cbd8105695c31ee5772fa87a0653bfbcb3ec940b` |
| `symbol:fuzzyroutines.Triangle`                                                     | editorial, mathematical | `sha256:af8829f7c333c896ec2715a5ccc4bf289a5c241e1c48b6ec150adb6c7bd97f94` | `sha256:da7963aecef62b0491483dbc5de134a1999f3fa42a0a26405591ff9926100638` |
| `symbol:fuzzyroutines.membership.MembershipScalar`                                  | editorial, mathematical | `sha256:ef9a8bb2f9f79e362679d96fc2d494231773bc40f588b74a6aedc90299911f8e` | `sha256:617eb81a84ce0c8ad50c05075381690062e83c98b3a82ab3443be93fcb4d6c52` |
| `page:guides`                                                                       | editorial, mathematical | `sha256:649ce49d1a56b58b0af5a24fd36f59f55aa8d4f75ee58cb1cdbf4fd650ab3c68` | `sha256:34d3890eace52777afa556a2c2cab74cb50546af1edde6dbc748b6e3c9c196fd` |
| `page:guides.alarm`                                                                 | editorial, mathematical | `sha256:9f4c0c4a3b98094640432468d29fd358770790cb89327d72aa7d56e981737593` | `sha256:c0a18434a56d22e2f4a9d453005387011035779cbff693e7ad30a3e7ef7b6648` |
| `page:guides.alpha-cuts`                                                            | editorial, mathematical | `sha256:1083328c7bd65b5b7fb88f2e313891e2c8629917a1cbee1c0cc77ee67b9f03d5` | `sha256:c01a45d3839bd1cdf7cc57922eae9b912f8e989d9c194c350348a1b3c016daad` |
| `page:guides.api-recipes`                                                           | editorial, mathematical | `sha256:6c9d01e1983d0b6081a4a944c3cd2ec357e076cb4b4ab42556ec50ee1eb50654` | `sha256:89ed8d2d694315b3952c685b9460ff72dcf76c9b4399f0f307ba4bb6207cbd36` |
| `page:guides.centroid`                                                              | editorial, mathematical | `sha256:06858aed49704931658d7fc622eec69b55de479540deb40b7215f4fdab64cd01` | `sha256:ce243befa79115a92dc3ff290bacde4b09a176a3a254998650548c287a3597e1` |
| `page:guides.custom`                                                                | editorial, mathematical | `sha256:6d7f1755ff6cf9404acdf0ff7e46d75a1acbe1a5cf903fba02fb4b80abc0498a` | `sha256:6e44d020632d7e95abf76d78334aa877cb4a84f89d7c1bc8b94a92dcd8338633` |
| `page:guides.figures`                                                               | editorial, mathematical | `sha256:d0e3689dfc53bffe722dca619f1bc7ed065afb4042398905d98b15b552326a1c` | `sha256:a7f74264a41a1db2db50119fd0363b489b6a5a4de954919b83a5d48fb1eb1a4d` |
| `page:guides.membership-families`                                                   | editorial, mathematical | `sha256:4c8e5be1db16ae6c0bd043656c4bf5d7491ae09c1e7c7bba780a66f24286ee00` | `sha256:8360bc7c2c166e8cd9bfe89547791b06c52f009d670f909a251dead9b14e8822` |
| `page:guides.risk`                                                                  | editorial, mathematical | `sha256:d25e2395a8aa98b3e5d2ac224d8c09a5497cfb4c5413db9c7fc263d8311bac4e` | `sha256:74d34cc6e7656224e153251265fb3a4301637deec79a5d08a8066a5027f7a8b1` |
| `page:guides.scale-audit`                                                           | editorial, mathematical | `sha256:eb4bd8c5e534bc02978be2ea3563229106dcbe19739fb99f4b30a7e4ae884f4a` | `sha256:e1f691762a089cdfcffdfcd7518d0428418487b08a78e7099d0cf987ec169081` |
| `page:guides.sensors`                                                               | editorial, mathematical | `sha256:039b6826a3d06368dd2b13ca029bd01d6ec8ec2ddd0cf0bd30180404fe308c1f` | `sha256:aaec182cd5174aa1013f2e7f54d2e457e92de3fd7bea449bb760e91525f9cf40` |
| `page:guides.temperature`                                                           | editorial, mathematical | `sha256:9e4533e8031512e2e6353d54cf4607e245bf21b1a2c88e8e1595430da0ecc1c8` | `sha256:09567c246fab61e6c1080752310e9eae1424ee74414f28d7a8e659ce644ddf04` |
| `page:quick-start`                                                                  | editorial, mathematical | `sha256:2a05f8feebea743b86a490c2dbff7fcdec52e84c8c90b62f6b83d3abd8687ae0` | `sha256:af17492b928b2f658f3087f79785dc386f116913e081fc5b5c3acfe42a09fa2e` |
| `page:guides.errors`                                                                | editorial, mathematical | `sha256:cd426d56df8d158dcbd49331bbcfa8cbae5055ff3d260a6b0811b255c241ddb1` | `sha256:a79578c5f0f911f353778aa7fc66c76382f722bbbfd9ee4863bf77605ac8fafa` |
| `page:guides.example-index`                                                         | editorial, mathematical | `sha256:fbdd2976385e015247f2d7e6b966073e394c4338374333b219e000770cc4135c` | `sha256:bc7083f99e8d1b89fbde79da9b951e8127e7388ff0c0909ec02a96b45e4e8449` |
| `page:guides.historical-recipes`                                                    | editorial, mathematical | `sha256:7e336948192b690fe2f042cd16d0df4ec7a4b4302946f0cf6d8279a1de688d41` | `sha256:16760b215fe7123de94ede23d8759665d998395a98447339a6bc23937c0ea4a2` |
| `page:guides.operators`                                                             | editorial, mathematical | `sha256:544e3a889535715fc43e226b1707b3a221e5bf86a0ce9f311a3fc2a9ad3225f5` | `sha256:e6d68c845c1def669e80ea7cde09738fc21a6fc9a1ff99d5bf23b2b6bb8a1d53` |
| `page:guides.results`                                                               | editorial, mathematical | `sha256:e6a5ef56bc602d8bd22f14a952e04a6ace9dbffe4d8ea90d9704d3beb01081c6` | `sha256:f24bfc8f937248376eb76b9e8148ff170b6b312fe0a4b8ac28406276a20cc0e8` |
| `page:guides.workflow`                                                              | editorial, mathematical | `sha256:be6d8d2ca92572df77c56568ce5e9c498ef419b04aecd3e78573235d5b3f2356` | `sha256:c048da486e10fd632bd41e115e06ee7eca0890ad99502e679f71318a1969a8e1` |
| `page:mathematics.alpha-cuts`                                                       | editorial, mathematical | `sha256:126c9ce07b5ce5a1647364910bae4e68e66df0624ad23f0979d0527c462ded5c` | `sha256:e0bba0e96bb1f864751189adc70857d6af3a9d7cba57769ea7ab0f1e197b45b4` |
| `page:mathematics.centroid-defuzzification`                                         | editorial, mathematical | `sha256:8d68169da3bfcf30b600a78f3b156be0764ac620346c13753e5a019466e1ff98` | `sha256:d3636b18f46d37435df1ecc8aef1273881040a519c6642259b4dd8878bd66476` |
| `page:mathematics.finite-number-policy`                                             | editorial, mathematical | `sha256:b540b154c6b228eb8b8e15ff0cc36bfaf380121f022ad4b345e4313f4aa1f8eb` | `sha256:98508ae044aafb692c7626e620cb0a1d8e3922525e266fbeacc603beb43abe6b` |
| `page:mathematics.fuzzy-set-convexity`                                              | editorial, mathematical | `sha256:dd0ad4d63e75ae782bfdd4b181bc012e91a8b98944311de130137b090773629a` | `sha256:ca6a19c67131062234ad1f298eedbbf9293e33c729a2d0357837198a2032ca96` |
| `page:mathematics.fuzzy-set-normalization`                                          | editorial, mathematical | `sha256:f348d817cd4dd739c47712fa2c2010151af8a2acad012ec45b8a1eb7721cf4fc` | `sha256:5c902defae644e45c66b50a09c86fda509aca4e95debaf89655eab25b3459a7a` |
| `page:mathematics.fuzzy-set-operations`                                             | editorial, mathematical | `sha256:20b5162f0aafce7787447062f7cb76c66086497188b1328a96b208d6c4786a29` | `sha256:6b1e7747ea642d7308cf820884de4e15c95700400052db7f87413a66ebacaa29` |
| `page:mathematics.fuzzy-set-relations`                                              | editorial, mathematical | `sha256:d3801584d3d407fa9d6418065504e8c4e8e1c9d5bcddf7ebfe40274c44ab4f1d` | `sha256:01d98a994069005b7836b99cc9a12c1e8958561eb900c6eae2cf126be81a1965` |
| `page:mathematics.linguistic-term-model`                                            | editorial, mathematical | `sha256:43a316c52cf6ace0a90f6a9e4bb12c750d2f0b76dd11d5036af28437d01edada` | `sha256:2514bee8f50127ea756b60c055629d2fe726f278fc5a8651f5c1754555d66acb` |
| `page:mathematics.membership-function-contracts`                                    | editorial, mathematical | `sha256:e12bce6edda6f8cebc01f20111c4f9fe1b9728b748b555dcd3007ac0c2b27053` | `sha256:6f2ca119f9757fd6082f5b8fae42f4a0dc65d8fcfba62da5f6cd48d84a7f3e35` |
| `page:mathematics.model`                                                            | editorial, mathematical | `sha256:cab9dc591f3e6903fa5adccab47ab29a75b01614402d6de85ea36aca806e877f` | `sha256:0929c57c3b43fc2ef65096c62c5ddb65aad1b7d8e4946f0f8ac1624b19a321f1` |
| `page:mathematics.numerical-edge-policy`                                            | editorial, mathematical | `sha256:8d87163a6dbccef9a8703a6eadf36ca18488e06f00a90e183984ed98329799cb` | `sha256:8072749fc9c21eaa6b9ad17ebac47948dffcaa231b79431246744fd197244efe` |
| `page:mathematics.parabolic-negation-derivation`                                    | editorial, mathematical | `sha256:cc84da31c9b4780bd2af15ce3cb756a3e8dfceab555860aa2c89e2a75ed048e7` | `sha256:5c938be09a62e96c1550b534ae7af913d3ba5ce2f51f3a8e14d00359d47fe808` |
| `page:mathematics.source-algorithm-invariants`                                      | editorial, mathematical | `sha256:ea8eab9de491df209ef41a4cae121eed67a46049cfbdf9b264f55fc0cbfe25a4` | `sha256:f7903eba439e53641305a804ff47d89bff88a3b08d93cd67b863cebf2f9a4c11` |
| `page:mathematics.universe-support-contract`                                        | editorial, mathematical | `sha256:f7cdde7d2d4e60ab8d7e13cf95381f783eda89e27628e9c05a28ad9707ad0954` | `sha256:6429d33f4d8fea3efa26af0e81810679993af41afd66d8092644c8c3297ea195` |
| `page:migration.1.0.3-to-2.0.0`                                                     | editorial, mathematical | `sha256:58cbf5c741e0b81718b2fb03b49b234db6a1bbba84ad966dd231b16a889584d7` | `sha256:ac483427ce3ac65e6fbaa12107426a46d690bfc5193bc1adc703f662c96766bb` |
| `page:migration.historical-to-modern`                                               | editorial, mathematical | `sha256:f42e5330774598e2e771473f047cc77c82aea2db207f82164270c6430d5b2360` | `sha256:9b853b828ce5ce110db60bd340d639423ee5c7665a9fbe75355191761886bb3d` |
| `module:fuzzyroutines`                                                              | editorial, mathematical | `sha256:7498f92d4ee713f0c6203cea02c65661d8d6e54a09a2c1b22544c527e8751ac8` | `sha256:67c399e36ad7ab9a3f4a7f49e8bce0b6e85ad376534ff72d607cae060cb8c43f` |
| `module:fuzzyroutines.FuzzyRoutines`                                                | editorial, mathematical | `sha256:8b4af731bd7f613019f442261c9c1cfb3f22d86527566c467d9ac30296a32e07` | `sha256:f691bf07146239b956aa485154bc3e46108d92ed13f2ea96d0bdcb1b2920cf4b` |
| `module:fuzzyroutines.alphacuts`                                                    | editorial, mathematical | `sha256:4d88e6ac30cb505b67e92fa96467edfa7c2785438a79d623828baf516a82264f` | `sha256:0000f23b742d8c8208ee874ab21deb0eed754e4a04bab5b3c9d8245893aacab8` |
| `module:fuzzyroutines.defuzzification`                                              | editorial, mathematical | `sha256:4b96b2e8605994707d1b488652d0554f93caa40c1ed077fb35036c95cc21af57` | `sha256:7e8ee0e269e7bc5af54094e09a1ca142e5e636ae49881d03bad26e94e4e17bef` |
| `module:fuzzyroutines.domain`                                                       | editorial, mathematical | `sha256:a0d7b9fde8473453c0f294811e6e452f533954b24fefdc69115cd9a3c5ef19fc` | `sha256:ddf481fe7f04b3998f7d47061f9a8fe744c7253562cf3df97ef8e7e37ea37968` |
| `module:fuzzyroutines.exceptions`                                                   | editorial, mathematical | `sha256:3102490786fccb08169491532eb628d0c91fdaa3ef226960ea7d6ca78f8358b5` | `sha256:24b525783066d14b6f90863763d75d714d6872efc9669d05e47ad38d9e062c45` |
| `module:fuzzyroutines.fuzzysets`                                                    | editorial, mathematical | `sha256:4c2b2a59efc196f10536851dedac8c22789793a88186ad520fa58fa3c927c1f3` | `sha256:ee52ce76f3932af4720a8ae19fa2e0d8bbbd098c4c1f29c683bc8ce95c30fb14` |
| `module:fuzzyroutines.linguistic`                                                   | editorial, mathematical | `sha256:96cb9619b6f611c210cfdb691e43e98710498a7087fb344ae02d1362763ac061` | `sha256:8535757c299b199c5f5575091c777da8a522bbe9697e8b9ead56cb3df43b54dc` |
| `module:fuzzyroutines.membership`                                                   | editorial, mathematical | `sha256:4fe6efe8eb3ba11dbc15cec23e038404f677b39a607eee972d0f9836e527bb39` | `sha256:4984c31c5125e385c88121aa3d7adcadea10b3e48d16d5cd39ab0a9a5cc67d85` |
| `module:fuzzyroutines.operators`                                                    | editorial, mathematical | `sha256:eb899d29e91d19e36c5cb2cb0eaf5b0cdbd117d2be4565259f646e4af6e19c5b` | `sha256:bfcefbb9a32e379a1db512d463887dddc535d9a27fc45c74681f308cf2e79d8a` |
| `module:fuzzyroutines.properties`                                                   | editorial, mathematical | `sha256:7c989f09299cd314c66cc9a70d48d0e4cfc44d10eb3046f18c5b22b0bd9805e7` | `sha256:14019594b96c53294b21ba1ea7001731e08d9fb2c80b55b266cb451d344862fd` |
| `module:fuzzyroutines.relations`                                                    | editorial, mathematical | `sha256:708b5dcd6e6626a6d8ca04b4f99535e62e6f6129c300032c0612df93a637fbd0` | `sha256:41d72006e93416ea456213143fbd4f9029cbeb437ffd8208b54151babad03a74` |
| `page:contracts.compatibility`                                                      | editorial, technical    | `sha256:aed41e3bc96dccb865f29894bfe7e966e3336676c9b241ef0cedd0080c6512b9` | `sha256:9258bfc0bda16e49d866cb11f370695e27b4ca4fe42b4aff46326c94ebe371d6` |
| `page:contracts.public-typing`                                                      | editorial, technical    | `sha256:0b05b3b0b3638306d97b75bf89738f9bb322309fcc20ce09daf83a03da4b6d5d` | `sha256:78301515cdab739e74528af26adabb57a02958f9f71faa8da7ed8da662772017` |
| `page:guides.universal-fuzzy-scale`                                                 | editorial, mathematical | `sha256:7092df9d1812256efb772ca9e8e586cdde462cb9395de08558bb439c345a2193` | `sha256:1b80e97feffcdf96a1f0e5196736f07be98e03ea7c787b4a67c21e051fc82687` |

## Fresh Universal Fuzzy Scale application review after PR #310

At **2026-10-10T18:09:44Z**, AIna-Dev performed a new scientific and Chinese editorial
review of `page:guides.universal-fuzzy-scale` after its cybersecurity/risk
application paragraphs changed in
[PR #310](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/310),
integrated as [`37ffc77`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/37ffc778afeae1fce12348485d21dfa17356d1ec).
This is a fresh, explicit AI acceptance under the maintainer's existing
zh-CN 2.0.0 delegation, not automatic approval of changed text or a claim of
human/native-speaker review. AIna-Dev performed both required roles.

The Chinese paragraphs preserve the English distinction between normalized
scores, linguistic grades and incident probabilities. They correctly explain
that increasing risk and improving protection have opposite decision meanings,
that all membership grades should accompany the selected label, and that
normalization, aggregation, domain validation, weak coverage and response
rules belong to the consuming application. The wording is scientifically
accurate and natural; no further prose correction was required. A targeted
check of the current historical API confirms score `0.75` selects `High` with
membership `1`, rather than asserting an incident probability. Protected code
and formulas are unchanged between the current English and Chinese page.

Only this unit's Chinese review records were refreshed; the root maintainer's
Russian records and all other Chinese units were preserved. The original UFS
row above remains historical evidence. The following **single current pair**
supersedes that row for active 2.0.0 acceptance:

- Unit: `page:guides.universal-fuzzy-scale`.
- Canonical source: `sha256:3e8d706a808f95a2faa1a98e83cf40e2d6666ba6466522204a139b8913f8da20`.
- Chinese translation: `sha256:888d672b0d829f408a93e9e08649b13e152dca4b1104a765b08d506bed7d88ca`.
- Roles: editorial and mathematical.
- Reviewer: `AIna-Dev (AI; maintainer-delegated zh-CN 2.0.0 scientific/editorial review)`.
- Reviewed at: `2026-10-10T18:09:44Z`.

The unchanged validator binds both hashes. Any subsequent edit again requires
explicit review; this supplement grants no blanket future approval.
