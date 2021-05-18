from aws_cdk import (
    aws_qldb as qldb
)

from aws_cdk.core import Construct, CfnOutput, Stack


class QldbStack(Stack):
    def __init__(self, scope: Construct, id: str, project_code: str, stage_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a QLDB ledger for use
        ledger_name = f'{project_code}-{stage_name}-audit-trail'
        ledger = qldb.CfnLedger(self, 'Ledger',
                                name=ledger_name,
                                permissions_mode='ALLOW_ALL')

        CfnOutput(self, "LedgerName", value=ledger.name)

        # qldb.CfnStream(self, 'LedgerStream')

        self._ledger = ledger

    @property
    def ledger_ref(self) -> qldb.CfnLedger:
        return self._ledger
