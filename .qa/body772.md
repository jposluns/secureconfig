Narrows TODO 1.297 for `elasticsearch.md`'s OpenSearch GCS/Azure client-side encryption reading by checking every OpenSearch release tag from 2.10.0 to 3.9.0.

## Change

- **Source read.** `BlobStoreRepository`, `MeteredBlobStoreRepository`, `EncryptedBlobStore`, `GoogleCloudStorageRepository` and `AzureRepository` were fetched at each of the 31 release tags from 2.10.0 to 3.9.0 (raw files from the tag, every fetch HTTP 200 from `raw.githubusercontent.com`), and are cited at the tag for 3.3.2, 3.4.0, 3.7.0 and 3.9.0 alongside the existing 2.10.0, 3.0.0 and 3.8.0 citations. Other files, including `CryptoSettings`, were read only at the tags their Sources entries name. `CryptoSettings.validate()` is cited only at 2.10.0, 3.0.0 and 3.8.0; its requirements at the other checked tags are not established here.
- **Wrap.** At all 25 tags from 2.10.0 to 3.3.2, `BlobStoreRepository.blobStore()` has the same body: it calls `createBlobStore` and wraps the result in `EncryptedBlobStore` when crypto metadata is present. From 3.4.0 to 3.9.0 it returns `blobStore(false)` through a `BlobStoreProvider`, which was not read across tags, so the wrap there rests only on the existing 3.8.0 citation and is not established at 3.4.0 to 3.7.0 or 3.9.0.
- **Overrides.** At every checked tag, `MeteredBlobStoreRepository`, `GoogleCloudStorageRepository` and `AzureRepository` declare no `blobStore()` method, and `AzureRepository` overrides `getBlobStore()` only to return `super.getBlobStore()`. From 3.7.0 GCS and Azure also override `getNativeStore()`; whether that path bypasses the wrap, and whether a deployment uses it, are not established.
- **Claims.** `os-gcs-azure-versions` (392 characters) and `os-gcs-azure-blobstore` (399) are revised, each stating that the wrap is unestablished at 3.4.0 to 3.7.0 and 3.9.0; new REASONED claims `os-gcs-azure-range` (392) and `os-gcs-azure-native` (320). The "earliest checked release" wording becomes the checked range; the "releases between those checked" qualifier is dropped for the five classes now read at every tag, not for other files, whose read tags the guide states.
- Four Sources entries and four source components (one per newly cited tag) added.
- TODO 1.297 narrowed to deployed encryption, installed key providers, releases before 2.10.0 and after 3.9.0, the `BlobStoreProvider` wrap at 3.4.0 to 3.7.0 and 3.9.0, and the native-store path. DONE.md has the partial 1.297 row.
- Header summaries and `body_sha256` regenerated; CHANGELOG, VERSION 1.0.772, plugin.json and both bundles updated.

## Checks

`tools/run_all_checks.sh` with the pinned parser (markdown-it-py 4.2.0) first on PATH: all gates passed. SKIPs in that host run: python3 3.14.4 versus CI's pinned 3.14.7, and the AIQT hook settings file absent (hooks not activated).
