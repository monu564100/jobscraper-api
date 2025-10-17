from typing import Optional
from pydantic import BaseModel, Field


class SearchJobsParams(BaseModel):
    site_names: Optional[str] = Field(default="indeed,linkedin")
    search_term: Optional[str] = Field(default="software engineer")
    location: Optional[str] = Field(default="")
    distance: Optional[int] = Field(default=None)
    job_type: Optional[str] = Field(default=None)
    google_search_term: Optional[str] = Field(default=None)
    results_wanted: Optional[int] = Field(default=20)
    easy_apply: Optional[bool] = Field(default=None)
    description_format: Optional[str] = Field(default=None)
    offset: Optional[int] = Field(default=None)
    hours_old: Optional[int] = Field(default=96)
    verbose: Optional[int] = Field(default=None)
    country_indeed: Optional[str] = Field(default=None)
    is_remote: Optional[bool] = Field(default=None)
    linkedin_fetch_description: Optional[bool] = Field(default=None)
    linkedin_company_ids: Optional[str] = Field(default=None)
    enforce_annual_salary: Optional[bool] = Field(default=None)
    proxies: Optional[str] = Field(default=None)
    ca_cert: Optional[str] = Field(default=None)
