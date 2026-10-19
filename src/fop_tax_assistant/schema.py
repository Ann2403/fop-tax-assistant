"""Extraction schema: a raw message from a sole proprietor (ФОП) -> structured request.

The same model is used for the LLM structured output, for validating every
response, and for the hand-labelled golden set in ``data/golden``.
Labelling rules for each field live in ``data/README.md``.
"""

import datetime as dt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Intent = Literal[
    "tax_question",
    "calculation",
    "declaration_prep",
    "deadline",
    "documents",
    "out_of_scope",
]

Topic = Literal[
    "tax_amount",
    "deadlines",
    "esv",
    "limits",
    "group_rules",
    "prro",
    "currency",
    "income_classification",
    "declaration",
    "vat",
    "other",
]

Currency = Literal["UAH", "USD", "EUR", "PLN", "other"]

CounterpartyType = Literal[
    "client_resident",
    "client_nonresident",
    "own_account",
    "individual",
    "bank",
    "tax_authority",
    "unknown",
]

MissingField = Literal["fop_group", "vat_payer", "period", "amounts", "transaction_dates"]

Language = Literal["uk", "ru", "en", "mixed"]


class Period(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year: int = Field(ge=2020, le=2030)
    quarter: int | None = Field(default=None, ge=1, le=4, description="null when only the year is mentioned")


class Transaction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: dt.date | None = Field(description="ISO date; relative dates resolved against received_at; null if unknown")
    amount: float = Field(gt=0, description="Always positive; the sign is carried by direction")
    currency: Currency
    direction: Literal["incoming", "outgoing"]
    counterparty_type: CounterpartyType
    description: str | None = Field(default=None, description="Short free-text note; not scored")


class FopRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: Intent
    fop_group: int | None = Field(ge=1, le=4, description="Only if stated in the text")
    vat_payer: bool | None = Field(description="Only if stated or unambiguous in the text")
    period: Period | None = Field(description="Reporting period the request is about; only if stated")
    transactions: list[Transaction]
    topics: list[Topic] = Field(description="What the user explicitly asks about")
    language: Language
    missing_fields: list[MissingField] = Field(description="Data required by the intent but absent from the text")
