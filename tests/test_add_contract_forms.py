"""Tests for add_contract_forms module."""
import pytest
from datetime import datetime
from src.pages.add_contract_forms import (
    parse_date,
    render_dual_energy_form,
    render_telephone_form,
    render_insurance_pno_form,
    render_insurance_habitation_form,
    render_electricity_form,
    render_gas_form,
)
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_streamlit():
    with patch("src.pages.add_contract_forms.st") as mock_st:
        # Setup mock return values for inputs
        mock_st.text_input.return_value = "Test Value"
        mock_st.number_input.return_value = 100.0
        mock_st.date_input.return_value = datetime(2023, 1, 1)
        mock_st.text_area.return_value = "Option 1\nOption 2"
        mock_st.checkbox.return_value = True

        # Mock columns to return a list of mocks
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2]

        # Mock tabs
        mock_tab1 = MagicMock()
        mock_tab2 = MagicMock()
        mock_st.tabs.return_value = [mock_tab1, mock_tab2]

        yield mock_st


def test_parse_date():
    assert parse_date("01/01/2023") == datetime(2023, 1, 1)
    assert parse_date("2023-01-01") == datetime(2023, 1, 1)
    assert isinstance(parse_date("invalid"), datetime)
    assert isinstance(parse_date(None), datetime)


def test_render_dual_energy_form(mock_streamlit):
    extracted_data = {
        "fournisseur": "EDF",
        "electricite": {"pdl": "123", "tarifs": {"abonnement_mensuel_ttc": 10}},
        "gaz": {"pce": "456", "tarifs": {"abonnement_mensuel_ttc": 20}},
    }

    data_elec, data_gaz = render_dual_energy_form(extracted_data)

    assert "provider" in data_elec
    assert "provider" in data_gaz
    assert mock_streamlit.tabs.called


def test_render_telephone_form(mock_streamlit):
    extracted_data = {
        "fournisseur": "Orange",
        "forfait_nom": "Open",
        "data_go": 50,
        "prix_mensuel": 29.99,
    }

    result = render_telephone_form(extracted_data)

    assert result["fournisseur"] == "Test Value"  # From mock
    assert result["prix_mensuel"] == 100.0  # From mock
    assert mock_streamlit.text_input.called


def test_render_insurance_pno_form(mock_streamlit):
    extracted_data = {
        "assureur": "AXA",
        "bien_assure": {"adresse": "Paris"},
        "garanties": {"incendie": 1000},
    }

    result = render_insurance_pno_form(extracted_data)

    assert result["assureur"] == "Test Value"
    assert result["garanties"]["incendie"] == 100.0
    assert mock_streamlit.number_input.called


def test_render_insurance_habitation_form(mock_streamlit):
    extracted_data = {
        "assureur": "Allianz",
        "bien_assure": {"adresse": "Lyon"},
        "tarifs": {"prime_annuelle_ttc": 200},
    }

    result = render_insurance_habitation_form(extracted_data)

    assert result["assureur"] == "Test Value"
    assert result["tarifs"]["prime_annuelle_ttc"] == 100.0
    assert mock_streamlit.checkbox.called


def test_render_electricity_form(mock_streamlit):
    extracted_data = {
        "fournisseur": "TotalEnergies",
        "electricite": {"pdl": "789"},
        "tarifs": {"prix_kwh_ttc": 0.15},
    }

    result = render_electricity_form(extracted_data)

    assert result["fournisseur"] == "Test Value"
    assert result["pdl"] == "Test Value"
    assert mock_streamlit.text_input.called


def test_render_gas_form(mock_streamlit):
    extracted_data = {
        "fournisseur": "Engie",
        "gaz": {"pce": "101"},
        "tarifs": {"prix_kwh_ttc": 0.08},
    }

    result = render_gas_form(extracted_data)

    assert result["fournisseur"] == "Test Value"
    assert result["pce"] == "Test Value"
    assert mock_streamlit.text_input.called
