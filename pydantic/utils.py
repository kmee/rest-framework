# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin

from odoo import fields, models

from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationInfo,
    field_validator,
    model_validator,
)


class PydanticOdooBaseModel(BaseModel):
    """Pydantic BaseModel for odoo record

    This aims to help to serialize Odoo record
    improving behavior like previous version:

    * Avoid False value on non boolean fields
    * Convert Datetime to Datetime timezone aware
    * using int type on many2one return the foreign key id
      (not the odoo record)
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    @staticmethod
    def _extract_types_from_union(field_type: Any) -> list[Any]:
        """Extract types from a Union, Optional, Annotated or simple type.

        Returns a list of types, excluding None.
        """
        if field_type is None:
            return []

        origin = get_origin(field_type)

        # If it's Annotated, extract the annotated type (first argument)
        if origin is Annotated:
            args = get_args(field_type)
            if args:
                # Recursively process the annotated type
                return PydanticOdooBaseModel._extract_types_from_union(args[0])
            return []

        # Check if it's a Union (Union[X, Y] or X | Y)
        if origin is Union or origin is type(Union) or origin is UnionType:
            # Extract Union arguments
            args = get_args(field_type)
            # Filter None and return remaining types
            return [arg for arg in args if arg is not type(None)]

        # Check if it's Optional (which is Union[T, None])
        if origin is type(None) or field_type is type(None):
            return []

        # If it's neither Union nor Annotated, return the type directly
        return [field_type]

    @classmethod
    def _field_accepts_int_type(cls, field_name: str) -> bool:
        """Check if the field accepts int type (including in Unions).

        Returns True if the field type is int or if any of the types
        in a Union is int.
        """
        annotations = cls.__annotations__
        if field_name not in annotations:
            return False

        field_type = annotations[field_name]
        types = cls._extract_types_from_union(field_type)

        # Check if any of the types is int
        return any(t is int or t == int for t in types)

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        context: Any | None = None,
        **kwargs,
    ):
        if context is None:
            context = {}

        if "odoo_records" not in context:
            context["odoo_records"] = {}

        return super().model_validate(
            obj,
            context=context,
            **kwargs,
        )

    @field_validator("*", mode="before")
    @classmethod
    def odoo_validator_before(cls, value: Any, info: ValidationInfo):
        odoo_record = info.context and info.context.get("odoo_records").get(
            info.config.get("title")
        )
        if odoo_record is not None:
            if info.field_name in odoo_record._fields:
                field = odoo_record._fields[info.field_name]
                if value is False and field.type != "boolean":
                    return None
                if field.type == "datetime":
                    # Get the timestamp converted to the client's timezone.
                    # This call also add the tzinfo into the datetime object
                    return fields.Datetime.context_timestamp(odoo_record, value)
                if field.type == "many2one":
                    if not value:
                        return None
                    # If the field accepts int (including in Unions like Optional[int]),
                    # return only the .id (not the complete odoo record)
                    if cls._field_accepts_int_type(info.field_name):
                        return value.id
                if field.type == "many2many":
                    if not value:
                        return None
                    return [item.id for item in value]
        return value

    @model_validator(mode="before")
    @classmethod
    def odoo_model_validator(cls, data: Any, info: ValidationInfo) -> Any:
        if isinstance(info.context, dict):
            info.context["odoo_records"][info.config.get("title")] = (
                data if isinstance(data, models.BaseModel) else None
            )
        return data
