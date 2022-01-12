# -*- coding: utf-8 -*-
"""
This module has functions for string manipulation specific to building emails and reports.
"""

import datetime

def create_citation(publication):
    """Build a human readable string describing the publication.
    
    Args:
        publication (dict): dictionary of a publication from PubMed's API
        
    Returns:
        publication_str (str): human readable string with authors names, publication date, title, journal, DOI, and PubMed id
    """
    publication_str = ""

    publication_str += ", ".join([auth["firstname"] + " " + auth["lastname"] for auth in publication["authors"]]) + "."
    publication_str += " {}.".format(str(publication["publication_date"]["year"]))
    publication_str += " {}.".format(publication["title"])
    publication_str += " {}.".format(publication["journal"])
    publication_str += " DOI:{}".format(publication["doi"])
    publication_str += " PMID:{}".format(publication["pubmed_id"])
    publication_str += " PMCID:{}".format(publication["PMCID"])
    
    return publication_str



def create_citations_for_author(authors_pubs, publication_dict):
    """Create a publication citation with cited grants for each publication in authors_pubs.
    
    Args:
        authors_pubs (dict): A dict where the keys are publication IDs associated with the author and the values are a set of any grants cited for the publication.
        publication_dict (dict): A dict where the keys are publication IDs and the values are attributes of the publication such as the authors.
        
    Returns:
        (str): A string of the citations and cited grants for each publication.
    """
    
    return "\n\n\n".join([create_citation(publication_dict[pub_id]) + "\n\nCited Grants:\n" + 
                             "\n".join([grant_id for grant_id in authors_pubs[pub_id]] if authors_pubs[pub_id] else ["None"]) 
                             for pub_id in authors_pubs])


    
def add_indention_to_string(string_to_indent):
    """Adds a \t character to the begining of every line in string_to_indent
    Args:
        string_to_indent (str): string to add tabs to
    
    Returns:
        (str): string with tabs at the begining of each line
    """
    
    return "\n".join(["\t" + line for line in string_to_indent.split("\n")])





def build_project_email_body(project_dict, publication_dict, pubs_by_author_dict):
    """Build the body of the email to send to the project lead.
    
    The email_template key for each project is expected to have <total_pubs> somewhere in 
    the string. This is replaced by the publications for each author and their cited grants.
    
    Args:
        project_dict (dict): dictionary where the keys are project names and the values are attributes for the projects such as the authors associated with the project.
        publication_dict (dict): dictionary with publication ids as the keys, schema matches the publications JSON file
        pubs_by_author_dict (dict): dictionary where the keys are authors and the values are a dictionary of pub_ids with thier associated grants.
    
    Returns:
        body (str): the body of the email to be sent
    """
    
    if "authors" in project_dict:
        pubs_string = "\n\n\n".join([author + ":\n" + create_citations_for_author(pubs_by_author_dict[author], publication_dict) for author in project_dict["authors"] if author in pubs_by_author_dict])
    else:
        pubs_string = "\n\n\n".join([author + ":\n" + create_citations_for_author(pubs_by_author_dict[author], publication_dict) for author in pubs_by_author_dict])
       
    body = project_dict["email_template"]
    body = body.replace("<total_pubs>", pubs_string)
    return body


def create_indented_project_report(project_dict, pubs_by_author_dict, publication_dict):
    """Create an indented project report for the project.
    
    If the project has authors then create a report of the publications found for only those authors.
    Otherwise create a report of the publications found for all authors.
    
    Args:
        project_dict (dict): dictionary where the keys are project names and the values are attributes for the projects such as the authors associated with the project.
        pubs_by_author_dict (dict): dictionary where the keys are authors and the values are a dictionary of pub_ids with thier associated grants.
        publication_dict (dict): dictionary with publication ids as the keys, schema matches the publications JSON file
    
    Returns:
        text_to_save (str): the indented project report
    """
    
    if "authors" in project_dict:
        text_to_save = add_indention_to_string("\n\n\n".join([author + ":\n" + 
                                                               add_indention_to_string(create_citations_for_author(pubs_by_author_dict[author], publication_dict)) 
                                                               for author in project_dict["authors"] if author in pubs_by_author_dict]))
    else:
        text_to_save = add_indention_to_string("\n\n\n".join([author + ":\n" + 
                                                               add_indention_to_string(create_citations_for_author(pubs_by_author_dict[author], publication_dict)) 
                                                               for author in pubs_by_author_dict]))
                                           
    return text_to_save




def create_email_dict_for_no_PMCID_pubs(publications_with_no_PMCID_list, config_file, to_email):
    """Create an email with the publications information in it.
    
    For each publication in publications_with_no_PMCID_list add it's information 
    to the body of an email. Pull the subject, from, and cc emails from the 
    config_dict, and to from to_email.
    
    Args:
        publications_with_no_PMCID_list (list): A list of dictionaries.
        [{"DOI":"publication DOI", "PMID": "publication PMID", "line":"short description of the publication", "Grants":"grants funding the publication"}]
        config_file (dict): dict with the same structure as the configuration JSON file
        
    Returns:
        email_messages (dict): keys and values match the email JSON file.
    """
    
    email_messages = {"creation_date" : str(datetime.datetime.now())[0:16]}
    
    pubs_string = "\n\n\n".join([dictionary["line"] + "\n\n" + 
                          "PMID: " + (dictionary["PMID"] if dictionary["PMID"] else "None") + "\n\n" + 
                          "Cited Grants:\n" + ("\n".join(dictionary["Grants"]) if dictionary["Grants"] else "None") for dictionary in publications_with_no_PMCID_list])
    
    body = config_file["email_template"]
    body = body.replace("<total_pubs>", pubs_string)
    
    email_messages["emails"] = [{"body":body,
                                 "subject":config_file["email_subject"],
                                 "from":config_file["from_email"],
                                 "to":to_email,
                                 "cc":",".join([email for email in config_file["cc_email"]])}]       
    
    return email_messages



def replace_body_magic_words(authors_pubs, authors_attributes, publication_dict):
    """Replace the magic words in email body with appropriate values.
    
    Args:
        authors_pubs (dict): A dict where the keys are publication IDs associated with the author and the values are a set of any grants cited for the publication.
        authors_attributes (dict): A dict where the keys are attributes associated with the author such as first and last name.
        publication_dict (dict): A dict where the keys are publication IDs and the values are attributes of the publication such as the authors.
        
    Returns:
        body (str): A string with the text for the body of the email to be sent to the author.
    """
    pubs_string = create_citations_for_author(authors_pubs, publication_dict)
    
    body = authors_attributes["email_template"]
    body = body.replace("<total_pubs>", pubs_string)
    body = body.replace("<author_first_name>", authors_attributes["first_name"])
    body = body.replace("<author_last_name>", authors_attributes["last_name"])
    
    return body







