<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# PyPI Trusted Publishing runbook

## Security boundary

`.github/workflows/release-pypi.yml` is the only repository workflow authorized
to publish `fuzzyroutines`. It obtains a short-lived PyPI credential through
GitHub OIDC. Do not create a `PYPI_TOKEN`, copy historical Travis credentials,
or add a username or password to the workflow.

Pull requests and manual dispatches are dry runs. They build, test, and
clean-install the distributions but cannot reach either the provenance or
publish jobs. Publication is possible only for an annotated stable tag whose
name and `pyproject.toml` version both equal `vX.Y.Z` / `X.Y.Z`.

## One-time GitHub configuration

An organization owner or repository administrator must configure these
controls in the GitHub web interface:

1. Create an environment named `pypi`.
2. Add the authorized release maintainers as required reviewers and prevent
   self-review when the available GitHub plan supports it.
3. Limit environment deployments to protected tags matching `v*`.
4. Create a tag ruleset targeting `v*`. Restrict tag creation to release
   maintainers and prevent tag update and deletion. Do not permit routine
   bypass of this ruleset.
5. Keep the repository or organization default workflow token permissions at
   read-only. The publish job requests only `id-token: write`; the separate
   provenance job additionally requests `attestations: write`.
6. Complete the PyPI configuration below, then create the repository variable
   `PYPI_TRUSTED_PUBLISHING_ENABLED` with the exact value `true`. Leave the
   variable absent until every other protection is verified.

The workflow also rejects lightweight tags, prerelease spellings, mismatched
package versions, and tag names other than the exact stable form `vX.Y.Z`.
Repository settings remain the authorization boundary; the workflow checks are
defence in depth.

The repository activation variable is an additional fail-closed switch, not a
substitute for required reviewers, tag protection, or PyPI's OIDC identity
binding. Removing it or setting any value other than `true` disables publishing.

## One-time PyPI configuration

An owner of the existing `fuzzyroutines` PyPI project must open **Manage →
Publishing** and register this GitHub Actions Trusted Publisher:

| PyPI field        | Required value        |
|-------------------|-----------------------|
| Owner             | `Fuzzy-Technologies`  |
| Repository        | `FuzzyRoutines`       |
| Workflow filename | `release-pypi.yml`    |
| Environment       | `pypi`                |

After a successful production release, remove any obsolete project-scoped API
tokens only after confirming they are not used by another approved workflow.
Never copy an old token into GitHub as a fallback.

## Pull-request and manual dry run

Every pull request to `develop` or `master` exercises the build and verification
jobs without requesting a publishing identity. After the workflow is merged, a
maintainer may also run **Trusted PyPI release → Run workflow** on an approved
branch. A manual run cannot publish, even after environment approval, because
both privileged jobs require a tag-push event.
The publish job additionally requires the explicit repository activation
variable described above.

The dry run must show all of the following:

- one wheel and one source distribution built from the same source revision;
- strict package metadata checks;
- recorded and verified SHA-256 hashes;
- the full deterministic suite on CPython 3.13 and 3.14;
- clean-install import smoke for both distributions.

## Production release

1. Complete `docs/release-readiness.md` with immutable evidence links.
2. Merge the reviewed release-version and release-note change through the
   normal protected branch process.
3. Confirm all required workflows are green for the exact release commit.
4. Create and push an annotated tag on that commit, for example:

   ```bash
   git tag -a v2.0.0 -m "Release FuzzyRoutines 2.0.0"
   git push origin v2.0.0
   ```

5. Review the GitHub environment deployment. Approve it only when the tag,
   package version, commit, changelog, test evidence, artifact names, and hashes
   agree.
6. After publication, record the immutable tag, workflow run, attestation,
   artifact hashes, and PyPI release URL in the release issue.

Never rerun publication for an existing PyPI version. Investigate a failed
release, increment the version through a new reviewed change when required, and
create a new protected annotated tag.

## Incident response

If an unauthorized or incorrect tag is created, do not approve the `pypi`
environment deployment. Preserve the workflow evidence, revoke the deployment
approval if still pending, and follow the repository incident process. PyPI
releases are immutable: use yanking for a published defective release and
publish a corrected new version; never replace uploaded files.
