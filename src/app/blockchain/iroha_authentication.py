import os
import sys
import binascii
from grpc import RpcError, StatusCode
import inspect  # inspect.stack(0)
from iroha import Iroha, IrohaGrpc, IrohaCrypto
from functools import wraps

from .utilities.errorCodes2Hr import get_proper_functions_for_commands

net = IrohaGrpc('127.0.0.1:50051')

class IrohaAuthentication:
    
    def trace(func):
        """
        A decorator for tracing methods' begin/end execution points
        """
        @wraps(func)
        def tracer(*args, **kwargs):
            name = func.__name__
            stack_size = int(len(inspect.stack(0)) / 2)  # @wraps(func) is also increasing the size
            indent = stack_size*'\t'
            print(f'{indent} > Entering "{name}": args: {args}')
            result = func(*args, **kwargs)
            print(f'{indent} < Leaving "{name}"')
            return result

        return tracer

    def get_commands_from_tx(transaction):
        commands_from_tx = []
        for command in transaction.payload.reduced_payload.__getattribute__("commands"):
            listed_fields = command.ListFields()
            commands_from_tx.append(listed_fields[0][0].name)
        return commands_from_tx

    @trace
    def send_transaction_and_print_status(private_key, src_account_id, transaction):
        hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
        creator_id = transaction.payload.reduced_payload.creator_account_id
        commands = IrohaAuthentication.get_commands_from_tx(transaction)
        print(f'Transaction "{commands}",'
              f' hash = {hex_hash}, creator = {creator_id}')

        iroha = Iroha(src_account_id)
        IrohaCrypto.sign_transaction(transaction, private_key)
        net.send_tx(transaction)

        for i, status in enumerate(net.tx_status_stream(transaction)):
            status_name, status_code, error_code = status
            print(f"{i}: status_name={status_name}, status_code={status_code}, "
                  f"error_code={error_code}")
            if status_name in ('STATEFUL_VALIDATION_FAILED', 'STATELESS_VALIDATION_FAILED', 'REJECTED'):
                error_code_hr = get_proper_functions_for_commands(commands)(error_code)
                raise RuntimeError(f"{status_name} failed on tx: "
                                   f"{transaction} due to reason {error_code}: "
                                   f"{error_code_hr}")

    def create_account(private_key, username, new_account_name, role_name):
        """
        Create a new user account
        """
        iroha = Iroha(username+"@pschain")

        created_private_key = IrohaCrypto.private_key()
        created_public_key = IrohaCrypto.derive_public_key(private_key)

        tx = iroha.transaction([
            iroha.command('CreateAccount', account_name=new_account_name,
                        domain_id="pschain", public_key=created_public_key),
            iroha.command('AppendRole', account_id=new_account_name+"@pschain",
                        role_name=role_name)
        ])
        IrohaAuthentication.send_transaction_and_print_status(private_key, username+"@pschain", tx)

        return created_private_key

    def create_asset(private_key, username, serial_number, amount):
        """
        Create a new asset
        """
        iroha = Iroha(username+"@pschain")
        tx = iroha.transaction([
            iroha.command('CreateAsset', asset_name=serial_number,
                        domain_id="pschain", precision=0),
            iroha.command('AddAssetQuantity', asset_id=serial_number+"#pschain",
                        amount=amount)
        ])
        IrohaAuthentication.send_transaction_and_print_status(private_key, username+"@pschain", tx)

    def subtract_asset(private_key, username, serial_number, amount):
        """
        Subtract from an existing asset
        """
        iroha = Iroha(username+"@pschain")
        tx = iroha.transaction([
            iroha.command('SubtractAssetQuantity', asset_id=serial_number+"#pschain",
                        amount=amount)
        ])
        IrohaAuthentication.send_transaction_and_print_status(private_key, username+"@pschain", tx)

    def transfer_asset(private_key, username, future_owner, serial_number, amount):
        """
        Move an existing asset
        """
        iroha = Iroha(username+"@pschain")
        tx = iroha.transaction([
            iroha.command('TransferAsset', src_account_id=username+"@pschain",
                        dest_account_id=future_owner+"@pschain", asset_id=serial_number+"#pschain",
                        description='init top up', amount=amount)
        ])
        IrohaAuthentication.send_transaction_and_print_status(private_key, username+"@pschain", tx)
