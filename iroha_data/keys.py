from iroha import IrohaCrypto

private_key = IrohaCrypto.private_key()
print("Private key: ", private_key)
print("Public key: ", IrohaCrypto.derive_public_key(private_key))