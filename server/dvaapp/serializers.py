from rest_framework import serializers
from django.contrib.auth.models import User
from models import Video, Frame, Region, DVAPQL, QueryResults, TEvent, IndexEntries, Tube, Segment, TrainedModel, \
    Retriever, SystemState, QueryRegion, QueryRegionResults, Worker, TrainingSet, RegionRelation, TubeRegionRelation, \
    TubeRelation, Export
import os, json, glob
from collections import defaultdict
from django.conf import settings


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class VideoSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Video
        fields = '__all__'


class ExportSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Export
        fields = '__all__'


class RetrieverSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Retriever
        fields = '__all__'


class TrainedModelSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = TrainedModel
        fields = '__all__'


class TrainingSetSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = TrainingSet
        fields = '__all__'


class WorkerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Worker
        fields = ('queue_name', 'id')


class FrameSerializer(serializers.HyperlinkedModelSerializer):
    media_url = serializers.SerializerMethodField()

    def get_media_url(self, obj):
        return "{}{}/frames/{}.jpg".format(settings.MEDIA_URL, obj.video_id, obj.frame_index)

    class Meta:
        model = Frame
        fields = ('url', 'media_url', 'video', 'frame_index', 'keyframe', 'w', 'h', 't',
                  'name', 'subdir', 'id', 'segment_index')


class SegmentSerializer(serializers.HyperlinkedModelSerializer):
    media_url = serializers.SerializerMethodField()

    def get_media_url(self, obj):
        return "{}{}/segments/{}.mp4".format(settings.MEDIA_URL, obj.video_id, obj.segment_index)

    class Meta:
        model = Segment
        fields = ('video', 'segment_index', 'start_time', 'end_time', 'metadata',
                  'frame_count', 'start_index', 'start_frame', 'end_frame', 'url', 'media_url', 'id')


class RegionSerializer(serializers.HyperlinkedModelSerializer):
    media_url = serializers.SerializerMethodField()

    def get_media_url(self, obj):
        if obj.materialized:
            return "{}{}/regions/{}.jpg".format(settings.MEDIA_URL, obj.video_id, obj.pk)
        else:
            return None

    class Meta:
        model = Region
        fields = ('url', 'media_url', 'region_type', 'video', 'user', 'frame', 'event', 'frame_index',
                  'segment_index', 'text', 'metadata', 'full_frame', 'x', 'y', 'h', 'w',
                  'polygon_points', 'created', 'object_name', 'confidence', 'materialized', 'png', 'id')


class RegionRelationSerializer(serializers.HyperlinkedModelSerializer):
    source_frame_media_url = serializers.SerializerMethodField()
    target_frame_media_url = serializers.SerializerMethodField()

    def get_source_frame_media_url(self, obj):
        if obj.source_region.frame_id:
            return "{}{}/frames/{}.jpg".format(settings.MEDIA_URL, obj.video_id, obj.source_region.frame_index)
        else:
            return None

    def get_target_frame_media_url(self, obj):
        if obj.target_region.frame_id:
            return "{}{}/frames/{}.jpg".format(settings.MEDIA_URL, obj.video_id, obj.target_region.frame_index)

    class Meta:
        model = RegionRelation
        fields = ('url', 'source_frame_media_url', 'source_frame_media_url', 'target_frame_media_url', 'video',
                  'source_region', 'target_region', 'name', 'weight', 'event', 'metadata', 'id')


class TubeRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TubeRelation
        fields = ('url', 'source_tube', 'target_tube', 'name', 'weight', 'video', 'event', 'metadata', 'id')


class TubeRegionRelationSerializer(serializers.HyperlinkedModelSerializer):
    region_frame_media_url = serializers.SerializerMethodField()

    def get_region_frame_media_url(self, obj):
        if obj.region.frame_id:
            return "{}{}/frames/{}.jpg".format(settings.MEDIA_URL, obj.video_id, obj.region.frame_index)

    class Meta:
        model = TubeRegionRelation
        fields = (
        'url', 'region_frame_media_url', 'region', 'tube', 'video', 'name', 'weight', 'event', 'metadata', 'id')


class TubeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Tube
        fields = '__all__'


class QueryRegionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = QueryRegion
        fields = '__all__'


class SystemStateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SystemState
        fields = '__all__'


class QueryResultsSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = QueryResults
        fields = '__all__'


class QueryRegionResultsSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = QueryRegionResults
        fields = '__all__'


class QueryResultsExportSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = QueryResults
        fields = '__all__'


class QueryRegionResultsExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryRegionResults
        fields = '__all__'


class QueryRegionExportSerializer(serializers.ModelSerializer):
    query_region_results = QueryRegionResultsExportSerializer(source='queryregionresults_set', read_only=True,
                                                              many=True)

    class Meta:
        model = QueryRegion
        fields = (
            'id', 'region_type', 'query', 'event', 'text', 'metadata', 'full_frame', 'x', 'y', 'h', 'w',
            'polygon_points',
            'created', 'object_name', 'confidence', 'png', 'query_region_results')


class TaskExportSerializer(serializers.ModelSerializer):
    query_results = QueryResultsExportSerializer(source='queryresults_set', read_only=True, many=True)
    query_regions = QueryRegionExportSerializer(source='queryregion_set', read_only=True, many=True)

    class Meta:
        model = TEvent
        fields = ('started', 'completed', 'errored', 'worker', 'error_message', 'video', 'operation', 'queue',
                  'created', 'start_ts', 'duration', 'arguments', 'task_id', 'parent', 'parent_process',
                  'imported', 'query_results', 'query_regions', 'id')


class TEventSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = TEvent
        fields = '__all__'


class IndexEntriesSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = IndexEntries
        fields = '__all__'


class RegionExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class RegionRelationExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionRelation
        fields = '__all__'


class TubeRelationExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TubeRelation
        fields = '__all__'


class TubeRegionRelationExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TubeRegionRelation
        fields = '__all__'


class FrameExportSerializer(serializers.ModelSerializer):
    region_list = RegionExportSerializer(source='region_set', read_only=True, many=True)

    class Meta:
        model = Frame
        fields = ('region_list', 'video', 'frame_index', 'keyframe', 'w', 'h', 't',
                  'name', 'subdir', 'id', 'segment_index')


class IndexEntryExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndexEntries
        fields = '__all__'


class TEventExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TEvent
        fields = '__all__'


class TubeExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tube
        fields = '__all__'


class SegmentExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = '__all__'


class DVAPQLSerializer(serializers.HyperlinkedModelSerializer):
    tasks = TaskExportSerializer(source='tevent_set', read_only=True, many=True)
    query_image_url = serializers.SerializerMethodField()

    def get_query_image_url(self, obj):
        if obj.process_type == DVAPQL.QUERY:
            return "{}queries/{}.png".format(settings.MEDIA_URL, obj.uuid)
        else:
            return None

    class Meta:
        model = DVAPQL
        fields = ('process_type', 'query_image_url', 'created', 'user', 'uuid', 'script', 'tasks',
                  'results_metadata', 'results_available', 'completed', 'id')


class VideoExportSerializer(serializers.ModelSerializer):
    frame_list = FrameExportSerializer(source='frame_set', read_only=True, many=True)
    segment_list = SegmentExportSerializer(source='segment_set', read_only=True, many=True)
    index_entries_list = IndexEntryExportSerializer(source='indexentries_set', read_only=True, many=True)
    event_list = TEventExportSerializer(source='tevent_set', read_only=True, many=True)
    tube_list = TubeExportSerializer(source='tube_set', read_only=True, many=True)
    region_relation_list = RegionRelationExportSerializer(source='regionrelation_set', read_only=True, many=True)

    class Meta:
        model = Video
        fields = ('name', 'length_in_seconds', 'height', 'width', 'metadata', 'frames', 'created', 'description',
                  'uploaded', 'dataset', 'uploader', 'segments', 'url', 'frame_list', 'segment_list',
                  'event_list', 'tube_list', 'index_entries_list', 'region_relation_list', "stream")


def import_frame_json(f, frame_index, event_id, video_id, w, h):
    regions = []
    df = Frame()
    df.video_id = video_id
    df.event_id = event_id
    df.w = w
    df.h = h
    df.frame_index = frame_index
    df.name = f['path']
    for r in f.get('regions', []):
        regions.append(import_region_json(r, frame_index, video_id, event_id))
    return df, regions


def import_region_json(r, frame_index, video_id, event_id, segment_index=None, frame_id=None):
    dr = Region()
    dr.frame_index = frame_index
    dr.video_id = video_id
    dr.event_id = event_id
    dr.object_name = r['object_name']
    dr.region_type = r.get('region_type', Region.ANNOTATION)
    dr.full_frame = r.get('full_frame', False)
    if segment_index:
        dr.segment_index = segment_index
    if frame_id:
        dr.frame_id = frame_id
    dr.x = r.get('x', 0)
    dr.y = r.get('y', 0)
    dr.w = r.get('w', 0)
    dr.h = r.get('h', 0)
    dr.confidence = r.get('confidence', 0.0)
    if r.get('text', None):
        dr.text = r['text']
    else:
        dr.text = ""
    dr.metadata = r.get('metadata', None)
    return dr


def create_event(e, v):
    de = TEvent()
    de.imported = True
    de.started = e.get('started', False)
    de.start_ts = e.get('start_ts', None)
    de.completed = e.get('completed', False)
    de.errored = e.get('errored', False)
    de.error_message = e.get('error_message', "")
    de.video_id = v.pk
    de.operation = e.get('operation', "")
    de.created = e['created']
    if 'seconds' in e:
        de.duration = e.get('seconds', -1)
    else:
        de.duration = e.get('duration', -1)
    de.arguments = e.get('arguments', {})
    de.task_id = e.get('task_id', "")
    return de


class VideoImporter(object):
    def __init__(self, video, video_json, root_dir):
        self.video = video
        self.json = video_json
        self.root = root_dir
        self.region_to_pk = {}
        self.region_relation_to_pk = {}
        self.frame_to_pk = {}
        self.event_to_pk = {}
        self.segment_to_pk = {}
        self.label_to_pk = {}
        self.tube_to_pk = {}
        self.name_to_shasum = {'inception': '48b026cf77dfbd5d9841cca3ee550ef0ee5a0751',
                               'facenet': '9f99caccbc75dcee8cb0a55a0551d7c5cb8a6836',
                               'vgg': '52723231e796dd06fafd190957c8a3b5a69e009c'}

    def import_video(self):
        if self.video.name is None or not self.video.name:
            self.video.name = self.json['name']
        self.video.frames = self.json['frames']
        self.video.height = self.json['height']
        self.video.width = self.json['width']
        self.video.segments = self.json.get('segments', 0)
        self.video.stream = self.json.get('stream', False)
        self.video.dataset = self.json['dataset']
        self.video.description = self.json['description']
        self.video.metadata = self.json['metadata']
        self.video.length_in_seconds = self.json['length_in_seconds']
        self.video.save()
        if not self.video.dataset:
            old_video_path = [fname for fname in glob.glob("{}/video/*.mp4".format(self.root))][0]
            new_video_path = "{}/video/{}.mp4".format(self.root, self.video.pk)
            os.rename(old_video_path, new_video_path)
        self.import_events()
        self.import_segments()
        self.bulk_import_frames()
        self.convert_regions_files()
        self.import_index_entries()
        self.bulk_import_region_relations()

    def import_segments(self):
        old_ids = []
        segments = []
        for s in self.json.get('segment_list', []):
            old_ids.append(s['id'])
            segments.append(self.create_segment(s))
        segment_ids = Segment.objects.bulk_create(segments, 1000)
        for i, k in enumerate(segment_ids):
            self.segment_to_pk[old_ids[i]] = k.id

    def create_segment(self, s):
        ds = Segment()
        ds.video_id = self.video.pk
        ds.segment_index = s.get('segment_index', '-1')
        ds.start_time = s.get('start_time', 0)
        ds.framelist = s.get('framelist', {})
        ds.end_time = s.get('end_time', 0)
        ds.metadata = s.get('metadata', "")
        if s.get('event', None):
            ds.event_id = self.event_to_pk[s['event']]
        ds.frame_count = s.get('frame_count', 0)
        ds.start_index = s.get('start_index', 0)
        return ds

    def import_events(self):
        old_ids = []
        children_ids = defaultdict(list)
        events = []
        for e in self.json.get('event_list', []):
            old_ids.append(e['id'])
            if 'parent' in e:
                children_ids[e['parent']].append(e['id'])
            events.append(create_event(e, self.video))
        event_ids = TEvent.objects.bulk_create(events, 1000)
        for i, k in enumerate(event_ids):
            self.event_to_pk[old_ids[i]] = k.id
        for old_id in old_ids:
            parent_id = self.event_to_pk[old_id]
            for child_old_id in children_ids[old_id]:
                ce = TEvent.objects.get(pk=self.event_to_pk[child_old_id])
                ce.parent_id = parent_id
                ce.save()

    def convert_regions_files(self):
        if os.path.isdir('{}/detections/'.format(self.root)):
            source_subdir = 'detections'  # temporary for previous version imports
            os.mkdir('{}/regions'.format(self.root))
        else:
            source_subdir = 'regions'
        convert_list = []
        for k, v in self.region_to_pk.iteritems():
            dd = Region.objects.get(pk=v)
            original = '{}/{}/{}.jpg'.format(self.root, source_subdir, k)
            temp_file = "{}/regions/d_{}.jpg".format(self.root, v)
            converted = "{}/regions/{}.jpg".format(self.root, v)
            if dd.materialized or os.path.isfile(original):
                try:
                    os.rename(original, temp_file)
                    convert_list.append((temp_file, converted))
                except:
                    raise ValueError("could not copy {} to {}".format(original, temp_file))
        for temp_file, converted in convert_list:
            os.rename(temp_file, converted)

    def import_index_entries(self):
        # previous_transformed = set()
        for i in self.json['index_entries_list']:
            di = IndexEntries()
            di.video = self.video
            di.algorithm = i['algorithm']
            # defaults only for backward compatibility
            if 'indexer_shasum' in i:
                di.indexer_shasum = i['indexer_shasum']
            elif i['algorithm'] in self.name_to_shasum:
                di.indexer_shasum = self.name_to_shasum[i['algorithm']]
            else:
                di.indexer_shasum = 'UNKNOWN'
            if 'approximator_shasum' in i:
                di.approximator_shasum = i['approximator_shasum']
            di.count = i['count']
            di.contains_detections = i['contains_detections']
            di.contains_frames = i['contains_frames']
            di.approximate = i['approximate']
            di.created = i['created']
            di.event_id = self.event_to_pk[i['event']]
            di.features_file_name = i['features_file_name']
            if 'entries_file_name' in i:
                entries = json.load(file('{}/indexes/{}'.format(self.root, i['entries_file_name'])))
            else:
                entries = i['entries']
            di.detection_name = i['detection_name']
            di.metadata = i.get('metadata', {})
            transformed = []
            for entry in entries:
                entry['video_primary_key'] = self.video.pk
                if 'detection_primary_key' in entry:
                    entry['detection_primary_key'] = self.region_to_pk[entry['detection_primary_key']]
                if 'frame_primary_key' in entry:
                    entry['frame_primary_key'] = self.frame_to_pk[entry['frame_primary_key']]
                transformed.append(entry)
            di.entries = transformed
            di.save()

    def bulk_import_frames(self):
        frame_regions = defaultdict(list)
        frames = []
        frame_index_to_fid = {}
        for i, f in enumerate(self.json['frame_list']):
            frames.append(self.create_frame(f))
            frame_index_to_fid[i] = f['id']
            if 'region_list' in f:
                for a in f['region_list']:
                    ra = self.create_region(a)
                    if 'id' in a:
                        frame_regions[i].append((ra, a['id']))
            elif 'detection_list' in f or 'annotation_list' in f:
                raise NotImplementedError, "Older format no longer supported"
        bulk_frames = Frame.objects.bulk_create(frames)
        regions = []
        regions_index_to_rid = {}
        region_index = 0
        bulk_regions = []
        for i, k in enumerate(bulk_frames):
            self.frame_to_pk[frame_index_to_fid[i]] = k.id
            for r, rid in frame_regions[i]:
                r.frame_id = k.id
                regions.append(r)
                regions_index_to_rid[region_index] = rid
                region_index += 1
                if len(regions) == 1000:
                    bulk_regions.extend(Region.objects.bulk_create(regions))
                    regions = []
        bulk_regions.extend(Region.objects.bulk_create(regions))
        for i, k in enumerate(bulk_regions):
            if regions_index_to_rid[i]:
                self.region_to_pk[regions_index_to_rid[i]] = k.id

    def bulk_import_region_relations(self):
        region_relations = []
        region_relations_index_to_fid = {}
        if 'region_relation_list' in self.json:
            for i, f in enumerate(self.json['region_relation_list']):
                region_relations.append(self.create_region_relation(f))
                region_relations_index_to_fid[i] = f['id']
            bulk_rr = RegionRelation.objects.bulk_create(region_relations)
            for i, k in enumerate(bulk_rr):
                self.region_relation_to_pk[region_relations_index_to_fid[i]] = k.id

    def create_region(self, a):
        da = Region()
        da.video_id = self.video.pk
        da.x = a['x']
        da.y = a['y']
        da.h = a['h']
        da.w = a['w']
        da.vdn_key = a['id']
        if 'text' in a:
            da.text = a['text']
        elif 'metadata_text' in a:
            da.text = a['metadata_text']
        if 'metadata' in a:
            da.metadata = a['metadata']
        elif 'metadata_json' in a:
            da.metadata = a['metadata_json']
        da.materialized = a.get('materialized', False)
        da.png = a.get('png', False)
        da.region_type = a['region_type']
        da.confidence = a['confidence']
        da.object_name = a['object_name']
        da.full_frame = a['full_frame']
        if a.get('event', None):
            da.event_id = self.event_to_pk[a['event']]
        if 'parent_frame_index' in a:
            da.frame_index = a['parent_frame_index']
        else:
            da.frame_index = a['frame_index']
        if 'parent_segment_index' in a:
            da.segment_index = a.get('parent_segment_index', -1)
        else:
            da.segment_index = a.get('segment_index', -1)
        return da

    def create_region_relation(self, a):
        da = RegionRelation()
        da.video_id = self.video.pk
        if 'metadata' in a:
            da.metadata = a['metadata']
        if 'weight' in a:
            da.weight = a['weight']
        if 'name' in a:
            da.name = a['name']
        if a.get('event', None):
            da.event_id = self.event_to_pk[a['event']]
        da.source_region_id = self.region_to_pk[a['source_region']]
        da.target_region_id = self.region_to_pk[a['target_region']]
        return da

    def create_frame(self, f):
        df = Frame()
        df.video_id = self.video.pk
        df.name = f['name']
        df.frame_index = f['frame_index']
        df.subdir = f['subdir']
        df.h = f.get('h', 0)
        df.w = f.get('w', 0)
        df.t = f.get('t', 0)
        if f.get('event', None):
            df.event_id = self.event_to_pk[f['event']]
        df.segment_index = f.get('segment_index', 0)
        df.keyframe = f.get('keyframe', False)
        return df

    def import_tubes(self, tubes, video_obj):
        # TODO: Implement this
        raise NotImplementedError
