# Verification of PR #8733 Reversion

This file serves as verification that PR #8733, which introduced the MongoDB extension, has been completely reverted.

After thorough investigation, we have confirmed:

1. The `src/mongodb` directory was completely removed from the repository.
2. The entry for `az mongo-db` was removed from `src/service_name.json`.
3. No traces of the standalone MongoDB extension remain in the codebase.

All changes from both commits in PR #8733 have been successfully reverted:
- Initial commit "mongodb cli" (acb09ba13a7433d45ec3c2bbc1207d50f40b354c)
- Follow-up commit "updating readme and adding examples" (7c2e1badafc8308b1bd085b0d0532a08d7d5139f)

Note: This verification file can be removed after review.