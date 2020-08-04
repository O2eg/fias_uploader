-----------------------
-- unique constraints
-----------------------
ALTER TABLE public.fias_addrob
    ADD CONSTRAINT fias_addrob_aoid_uq UNIQUE(aoid);
ALTER TABLE public.fias_house
    ADD CONSTRAINT fias_house_centerstid_uq UNIQUE(houseid);
ALTER TABLE public.fias_room
    ADD CONSTRAINT fias_room_rmtypeid_uq UNIQUE(roomid);
ALTER TABLE public.fias_stead
    ADD CONSTRAINT fias_stead_strstatid_uq UNIQUE(steadid);
ALTER TABLE public.fias_nordoc
    ADD CONSTRAINT fias_nordoc_uq UNIQUE(normdocid, docnum, docimgid);

---

ALTER TABLE public.fias_dict_actstat
    ADD CONSTRAINT fias_dict_actstat_actstatid_uq UNIQUE(actstatid);
ALTER TABLE public.fias_dict_centerst
    ADD CONSTRAINT fias_dict_centerst_centerstid_uq UNIQUE(centerstid);
ALTER TABLE public.fias_dict_roomtype
    ADD CONSTRAINT fias_dict_roomtype_rmtypeid_uq UNIQUE(rmtypeid);
ALTER TABLE public.fias_dict_strstat
    ADD CONSTRAINT fias_dict_strstat_strstatid_uq UNIQUE(strstatid);
ALTER TABLE public.fias_dict_operstat
    ADD CONSTRAINT fias_dict_operstat_operstatid_uq UNIQUE(operstatid);
ALTER TABLE public.fias_dict_eststat
    ADD CONSTRAINT fias_dict_eststat_eststatid_uq UNIQUE(eststatid);
ALTER TABLE public.fias_dict_ndoctype
    ADD CONSTRAINT fias_dict_ndoctype_ndtypeid_uq UNIQUE(ndtypeid);
ALTER TABLE public.fias_dict_flattype
    ADD CONSTRAINT fias_dict_flattype_fltypeid_uq UNIQUE(fltypeid);
ALTER TABLE public.fias_dict_currentstid
    ADD CONSTRAINT fias_dict_currentstid_curentstid_uq UNIQUE(curentstid);
ALTER TABLE public.fias_dict_socrbase
    ADD CONSTRAINT fias_dict_socrbase_kod_t_st_uq UNIQUE(kod_t_st);


-----------------------
-- Hash indexes
-----------------------
CREATE INDEX
    ON public.fias_addrob USING hash (aoguid);

CREATE INDEX
    ON public.fias_addrob USING hash (parentguid);

CREATE INDEX
    ON public.fias_addrob USING hash (previd);

CREATE INDEX
    ON public.fias_addrob USING hash (nextid);

CREATE INDEX
    ON public.fias_addrob USING hash (normdoc);

CREATE INDEX
    ON public.fias_house USING hash (houseguid);

CREATE INDEX
    ON public.fias_house USING hash (aoguid);

CREATE INDEX
    ON public.fias_house USING hash (normdoc);

CREATE INDEX
    ON public.fias_room USING hash (roomguid);

CREATE INDEX
    ON public.fias_room USING hash (houseguid);

CREATE INDEX
    ON public.fias_room USING hash (previd);

CREATE INDEX
    ON public.fias_room USING hash (nextid);   

CREATE INDEX
    ON public.fias_nordoc USING hash (normdocid);

CREATE INDEX
    ON public.fias_stead USING hash (steadguid);

CREATE INDEX
    ON public.fias_stead USING hash (parentguid);

CREATE INDEX
    ON public.fias_stead USING hash (previd);

CREATE INDEX
    ON public.fias_stead USING hash (nextid);

CREATE INDEX
    ON public.fias_stead USING hash (normdoc);
