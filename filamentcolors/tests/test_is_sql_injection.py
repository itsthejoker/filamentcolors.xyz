import pytest

from filamentcolors.helpers import is_sql_injection

# all of these examples are shit that's been aimed at the site
@pytest.mark.parametrize("url,expected", [
    # --- happy paths: empty, real URLs, and normal English notes ---
    ("http://example.com", False),
    ("", False),
    ("https://example.com/product/4?abc=d", False),
    ("https://www.amazon.com/dp/B08XYZ1234?ref=abc", False),
    ("https://shop.example.com/products/galaxy-black-pla", False),
    ("Please update this link, the old one is dead.", False),
    ("The old store closed, please remove this listing.", False),
    ("This filament has been discontinued, sorry!", False),
    ("I couldn't find a replacement anywhere.", False),
    ("Try the union store downtown, they have great colors.", False),
    ("Please select the correct variant on the product page.", False),
    # notes with a lone apostrophe/possessive/decade must still be allowed
    ("I couldn't find this one, it's gone from Bob's shop.", False),
    ("These were the 90's colors, no longer sold.", False),
    ("""1*if(now()=sysdate(),sleep(15),0)""", True),
    ("""10'XOR(1*if(now()=sysdate(),sleep(15),0))XOR'Z""", True),
    ("""1""", True),
    ("""10"XOR(1*if(now()=sysdate(),sleep(15),0))XOR"Z""", True),
    ("""(select(0)from (select(sleep(15)))v) / *'+(select(0)from(select(sleep(15)))v)+'"+(select(0)from(select(sleep(15)))v)+" * / """,
     True),
    ("""1-1; waitfor delay '0:0:15' --""", True),
    ("""1-1); waitfor delay '0:0:15' --""", True),
    ("""1-1 waitfor delay '0:0:15' --""", True),
    ("""18ZqgQO4z'; waitfor delay '0:0:15' --""", True),
    ("""1-1 OR 798=(SELECT 798 FROM PG_SLEEP(15))--""", True),
    ("""1-1) OR 369=(SELECT 369 FROM PG_SLEEP(15))--""", True),
    ("""1-1)) OR 680=(SELECT 680 FROM PG_SLEEP(15))--""", True),
    ("""1gpIIw1kM' OR 430=(SELECT 430 FROM PG_SLEEP(15))--""", True),
    ("""1sBDMSCAZ') OR 69=(SELECT 69 FROM PG_SLEEP(15))--""", True),
    ("""1RBz2eCMQ')) OR 196=(SELECT 196 FROM PG_SLEEP(15))--""", True),
    ("""1*DBMS_PIPE.RECEIVE_MESSAGE(CHR(99)||CHR(99)||CHR(99),15)""", True),
    ("""1'||DBMS_PIPE.RECEIVE_MESSAGE(CHR(98)||CHR(98)||CHR(98),15)||'""", True),
    ("""1'\"""", True),
    ("""1����%2527%2522\'\"""", True),
    ("""1*if(now()=sysdate(),sleep(15),0)""", True),
    ("""10'XOR(1*if(now()=sysdate(),sleep(15),0))XOR'Z""", True),
    ("""10"XOR(1*if(now()=sysdate(),sleep(15),0))XOR"Z""", True),
    ("""(select(0)from(select(sleep(15)))v)/*'+(select(0)from(select(sleep(15)))v)+'"+(select(0)from(select(sleep(15)))v)+"*/""",
     True),
    ("@@i3LWm", True),
    # --- classic UNION-based extraction ---
    ("""' UNION SELECT username, password FROM users--""", True),
    ("""-1) UNION SELECT 1,2,3--""", True),
    ("""' UNION ALL SELECT NULL,NULL,NULL--""", True),
    ("""1 UNION SELECT NULL,concat(table_name) FROM information_schema.tables""", True),
    # --- boolean-based / tautology ---
    ("""' OR '1'='1""", True),
    ("""' OR ''='""", True),
    ("""1 OR 1=1""", True),
    ("""1' AND 1=1--""", True),
    ("""admin'--""", True),
    # --- stacked queries / destructive ---
    ("""1; DROP TABLE swatches;--""", True),
    ("""'; DROP TABLE users; --""", True),
    ("""'; DELETE FROM swatch WHERE 1=1;--""", True),
    ("""1 INTO OUTFILE '/tmp/x'""", True),
    # --- command execution ---
    ("""1'; EXEC xp_cmdshell('dir');--""", True),
    ("""'; EXEC('SELECT 1')--""", True),
    # --- error-based / function abuse ---
    ("""1 AND extractvalue(1,concat(0x7e,version()))""", True),
    ("""1 AND updatexml(1,concat(0x7e,user()),1)""", True),
    ("""'||(SELECT LOAD_FILE('/etc/passwd'))||'""", True),
    ("""SELECT * FROM information_schema.tables""", True),
    # --- time-based (alternate phrasings) ---
    ("""1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--""", True),
    ("""1 AND BENCHMARK(1000000,MD5('a'))""", True),
])
def test_is_sql_injection(url, expected):
    assert is_sql_injection(url) == expected
