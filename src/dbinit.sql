--
-- PostgreSQL database dump
--

-- Dumped from database version 12.1
-- Dumped by pg_dump version 12.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: board; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.board (
    post_id integer NOT NULL,
    board_id integer NOT NULL,
    body character varying(1024) NOT NULL,
    author_user_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    deleted boolean DEFAULT false NOT NULL
);


--
-- Name: board_post_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.board_post_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: board_post_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.board_post_id_seq OWNED BY public.board.post_id;


--
-- Name: boardinfo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.boardinfo (
    board_id integer NOT NULL,
    name character varying(1024) NOT NULL,
    owner_user_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    deleted boolean DEFAULT false NOT NULL
);


--
-- Name: boardinfo_board_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.boardinfo_board_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: boardinfo_board_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.boardinfo_board_id_seq OWNED BY public.boardinfo.board_id;


--
-- Name: csrftoken; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.csrftoken (
    session_id character varying(32) NOT NULL,
    token character varying(32) NOT NULL
);


--
-- Name: session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.session (
    session_id character varying(32) NOT NULL,
    user_id integer NOT NULL,
    expire_at timestamp without time zone DEFAULT (now() + '1 day'::interval) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: userinfo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.userinfo (
    user_id integer NOT NULL,
    name character varying(128) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    password_hash character varying(128) NOT NULL,
    deleted boolean DEFAULT false NOT NULL
);


--
-- Name: userinfo_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.userinfo_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: userinfo_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.userinfo_user_id_seq OWNED BY public.userinfo.user_id;


--
-- Name: board post_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.board ALTER COLUMN post_id SET DEFAULT nextval('public.board_post_id_seq'::regclass);


--
-- Name: boardinfo board_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.boardinfo ALTER COLUMN board_id SET DEFAULT nextval('public.boardinfo_board_id_seq'::regclass);


--
-- Name: userinfo user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.userinfo ALTER COLUMN user_id SET DEFAULT nextval('public.userinfo_user_id_seq'::regclass);


--
-- Name: board board_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.board
    ADD CONSTRAINT board_pkey PRIMARY KEY (post_id);


--
-- Name: boardinfo boardinfo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.boardinfo
    ADD CONSTRAINT boardinfo_pkey PRIMARY KEY (board_id);


--
-- Name: csrftoken csrf_token_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.csrftoken
    ADD CONSTRAINT csrf_token_pkey PRIMARY KEY (session_id);


--
-- Name: session session_session_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_session_id_key UNIQUE (session_id);


--
-- Name: userinfo userinfo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.userinfo
    ADD CONSTRAINT userinfo_pkey PRIMARY KEY (user_id);


--
-- Name: board board_author_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.board
    ADD CONSTRAINT board_author_user_id_fkey FOREIGN KEY (author_user_id) REFERENCES public.userinfo(user_id);


--
-- Name: board board_board_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.board
    ADD CONSTRAINT board_board_id_fkey FOREIGN KEY (board_id) REFERENCES public.boardinfo(board_id);


--
-- Name: boardinfo boardinfo_owner_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.boardinfo
    ADD CONSTRAINT boardinfo_owner_user_id_fkey FOREIGN KEY (owner_user_id) REFERENCES public.userinfo(user_id);


--
-- Name: csrftoken csrftoken_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.csrftoken
    ADD CONSTRAINT csrftoken_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.session(session_id);


--
-- Name: session session_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.userinfo(user_id);


--
-- PostgreSQL database dump complete
--

