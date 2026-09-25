# Development

## Releasing

1. Make sure the release changes are merged into `main`.
2. Run the local checks:

   ```bash
   ./scripts/test
   ./scripts/lint
   ```

3. Open the **Actions** tab and run **Prepare Release**.
4. Enter the integration version without the `v` prefix, for example `1.3.6`.
5. Review the generated `release/v1.3.6` pull request. It updates the `version` property in `custom_components/bureau_of_meteorology/manifest.json`.
6. Merge the release pull request.
7. After the merge, Release Drafter creates or updates the release draft. Check that its version is `v1.3.6`.
8. Publish the release draft. Publishing creates the `v1.3.6` tag.
9. Confirm that the **Validate Release** workflow passes. It checks that the release tag matches the version in `manifest.json`.

Do not publish a release if the tag and manifest versions differ. Prepare a corrective release pull request first.
